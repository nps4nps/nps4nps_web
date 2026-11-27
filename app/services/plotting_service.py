import json
import math

import branca.colormap as cm
import folium
import pandas as pd


def create_sampling_map(data: pd.DataFrame) -> str:
    """Plot sampling coordinates and information on map"""

    def _basemap(df: pd.DataFrame) -> folium.Map:
        m = folium.Map(
            location=[df["lat"].mean(), df["lng"].mean()],
            zoom_start=8,
            tiles=None,
        )

        folium.TileLayer(
            tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            attr="Map data: &copy; OpenStreetMap contributors, SRTM | "
            "Map style: &copy; OpenTopoMap (CC-BY-SA)",
            name="Topographic map",
            max_zoom=17,
        ).add_to(m)

        folium.TileLayer(
            "OpenStreetMap",
            name="Street map",
            show=False,
        ).add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)

        return m

    def _altitude(df: pd.DataFrame) -> folium.LinearColormap:
        """Colour scale for altitude"""
        m = cm.LinearColormap(
            colors=["#2c7bb6", "#ffffbf", "#d7191c"],
            vmin=df["altitude"].min(),
            vmax=df["altitude"].max(),
            caption="Altitude (m)",
        )
        m.add_to(m)
        return m

    def _cards(df: pd.DataFrame, cm: folium.LinearColormap) -> list:
        """Prepare one info card per sample"""
        cards = []
        for _, row in df.iterrows():
            if pd.isna(row["altitude"]):
                altitude = None
                altitude_text = "unknown"
                colour = "#999999"
            else:
                altitude = float(row["altitude"])
                altitude_text = f"{int(altitude)} m"
                colour = cm(altitude)

            if pd.isna(row["date"]):
                year = None
            else:
                year = int(row["date"].year)

            popup_html = f"""
<b>{row['label']}</b>
<br>
Biome: <a href="{row['ecosystem']}" target="_blank">{row['ecosystem_label']}</a>
<br>
Sample material: <a href="{row['material']}" target="_blank">{row['material_label']}</a>
<br>
Altitude: {altitude_text}
<br>
Sampling date: {row['date']}
<br>
<a href="{row['np']}" target="_blank">See nanopublication ...</a>
"""

            cards.append(
                {
                    "lat": float(row["lat"]),
                    "lng": float(row["lng"]),
                    "altitude": altitude,
                    "biome": row["ecosystem_label"],
                    "date": str(row["date"]),
                    "year": year,
                    "colour": colour,
                    "popup": popup_html,
                    "tooltip": f"{row['ecosystem_label']}, {altitude_text}",
                }
            )

        return cards

    def _ranges(df: pd.DataFrame) -> dict:
        """Define ranges for slides etc"""
        alt_min = int(math.floor(df["altitude"].min() / 10) * 10)
        alt_max = int(math.ceil(df["altitude"].max() / 10) * 10)

        years = df["date"].dt.year.dropna()
        year_min = int(min(2000, years.min()) if not years.empty else 2000)
        year_max = int(max(2026, years.max()) if not years.empty else 2026)

        biome_counts = df["ecosystem_label"].value_counts()
        biome_checkboxes = ""
        for biome in sorted(biome_counts.index):
            count = biome_counts[biome]
            biome_checkboxes += f"""
          <label style="display: block;">
            <input type="checkbox" class="biome-box" value="{biome}" checked>
            {biome} ({count})
          </label>"""

        return {
            "alt_min": alt_min,
            "alt_max": alt_max,
            "year_min": year_min,
            "year_max": year_max,
            "biome_checkboxes": biome_checkboxes,
        }

    def _panel_html() -> str:
        return """
<div id="filter-panel" style="
    position: fixed; bottom: 30px; left: 10px; z-index: 1000;
    background: white; padding: 10px 14px; border-radius: 6px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.4);
    font-family: sans-serif; font-size: 13px; width: 260px;
    max-height: 80vh; overflow-y: auto;">

  <b>Filter by altitude</b>
  <br><br>

  Min: <span id="alt-min-label"></span> m
  <input type="range" id="alt-min" style="width: 100%;"
         min="__ALT_MIN__" max="__ALT_MAX__" step="10" value="__ALT_MIN__">

  Max: <span id="alt-max-label"></span> m
  <input type="range" id="alt-max" style="width: 100%;"
         min="__ALT_MIN__" max="__ALT_MAX__" step="10" value="__ALT_MAX__">

  <hr>

  <b>Filter by sampling year</b>
  <br><br>

  From: <span id="year-min-label"></span>
  <input type="range" id="year-min" style="width: 100%;"
         min="__YEAR_MIN__" max="__YEAR_MAX__" step="1" value="__YEAR_MIN__">

  To: <span id="year-max-label"></span>
  <input type="range" id="year-max" style="width: 100%;"
         min="__YEAR_MIN__" max="__YEAR_MAX__" step="1" value="__YEAR_MAX__">

  <hr>

  <b>Filter by biome</b>
  <button id="biome-all" style="margin-left: 8px;">All</button>
  <button id="biome-none">None</button>
  <br><br>
  __BIOME_CHECKBOXES__

  <hr>
  <b><span id="sample-count"></span></b>
</div>
"""

    def _filter_js() -> str:
        return """
<script>
window.addEventListener("load", function () {

    var map = __MAP_NAME__;
    var samples = __SAMPLES__;
    var markers = [];
    var allMarkerObjects = [];

    // (a) create one marker per sample and remember it
    for (var i = 0; i < samples.length; i++) {
        var sample = samples[i];

        var marker = L.circleMarker([sample.lat, sample.lng], {
            radius: 8,
            color: "black",
            weight: 1,
            fillColor: sample.colour,
            fillOpacity: 0.9
        });
        marker.bindPopup(sample.popup, { maxWidth: 300 });
        marker.bindTooltip(sample.tooltip);
        marker.addTo(map);

        markers.push({ marker: marker, sample: sample });
        allMarkerObjects.push(marker);
    }

    // zoom the map so that all samples are visible
    map.fitBounds(L.featureGroup(allMarkerObjects).getBounds(), { padding: [40, 40] });

    // (b) find the elements in the panel
    var minSlider = document.getElementById("alt-min");
    var maxSlider = document.getElementById("alt-max");
    var minLabel = document.getElementById("alt-min-label");
    var maxLabel = document.getElementById("alt-max-label");
    var yearMinSlider = document.getElementById("year-min");
    var yearMaxSlider = document.getElementById("year-max");
    var yearMinLabel = document.getElementById("year-min-label");
    var yearMaxLabel = document.getElementById("year-max-label");
    var countLabel = document.getElementById("sample-count");
    var biomeBoxes = document.getElementsByClassName("biome-box");
    var allButton = document.getElementById("biome-all");
    var noneButton = document.getElementById("biome-none");

    // (c) show only markers that pass ALL filters
    function applyFilter() {

        // --- altitude range ---
        var minAlt = Number(minSlider.value);
        var maxAlt = Number(maxSlider.value);

        if (minAlt > maxAlt) {
            maxSlider.value = minAlt;
            maxAlt = minAlt;
        }

        minLabel.textContent = minAlt;
        maxLabel.textContent = maxAlt;

        // --- sampling year range ---
        var minYear = Number(yearMinSlider.value);
        var maxYear = Number(yearMaxSlider.value);

        if (minYear > maxYear) {
            yearMaxSlider.value = minYear;
            maxYear = minYear;
        }

        yearMinLabel.textContent = minYear;
        yearMaxLabel.textContent = maxYear;

        // --- which biomes are ticked? ---
        var activeBiomes = [];
        for (var i = 0; i < biomeBoxes.length; i++) {
            if (biomeBoxes[i].checked) {
                activeBiomes.push(biomeBoxes[i].value);
            }
        }

        // --- go through all markers ---
        var visible = 0;

        for (var i = 0; i < markers.length; i++) {
            var sample = markers[i].sample;

            var altitudeOk = (sample.altitude === null) ||
                             (sample.altitude >= minAlt && sample.altitude <= maxAlt);
            var biomeOk = activeBiomes.includes(sample.biome);
            var yearOk = (sample.year === null) ||
                         (sample.year >= minYear && sample.year <= maxYear);

            if (altitudeOk && biomeOk && yearOk) {
                markers[i].marker.addTo(map);
                visible = visible + 1;
            } else {
                map.removeLayer(markers[i].marker);
            }
        }

        countLabel.textContent = visible + " of " + markers.length + " samples shown";
    }

    // (d) run the filter whenever something changes, and once at the start
    minSlider.addEventListener("input", applyFilter);
    maxSlider.addEventListener("input", applyFilter);
    yearMinSlider.addEventListener("input", applyFilter);
    yearMaxSlider.addEventListener("input", applyFilter);

    for (var i = 0; i < biomeBoxes.length; i++) {
        biomeBoxes[i].addEventListener("change", applyFilter);
    }

    allButton.addEventListener("click", function () {
        for (var i = 0; i < biomeBoxes.length; i++) {
            biomeBoxes[i].checked = true;
        }
        applyFilter();
    });

    noneButton.addEventListener("click", function () {
        for (var i = 0; i < biomeBoxes.length; i++) {
            biomeBoxes[i].checked = false;
        }
        applyFilter();
    });

    applyFilter();
});
</script>
"""

    basemap = _basemap(data)
    colormap = _altitude(data)
    samples = _cards(data, colormap)
    ranges = _ranges(data)
    panel_html = _panel_html()
    filter_js = _filter_js()

    panel_html = panel_html.replace("__ALT_MIN__", str(ranges["alt_min"]))
    panel_html = panel_html.replace("__ALT_MAX__", str(ranges["alt_max"]))
    panel_html = panel_html.replace("__YEAR_MIN__", str(ranges["year_min"]))
    panel_html = panel_html.replace("__YEAR_MAX__", str(ranges["year_max"]))
    panel_html = panel_html.replace(
        "__BIOME_CHECKBOXES__", str(ranges["biome_checkboxes"])
    )

    filter_js = filter_js.replace("__MAP_NAME__", basemap.get_name())
    filter_js = filter_js.replace("__SAMPLES__", json.dumps(samples))

    basemap.get_root().html.add_child(folium.Element(panel_html))
    basemap.get_root().html.add_child(folium.Element(filter_js))

    return basemap.get_root().render()
