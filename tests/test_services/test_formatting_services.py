import pandas as pd
import pytest

from app.services.formatting_services import (
    parse_date,
    parse_iso_coordinates,
    parse_label,
)


def test_parse_iso_coor_success():
    lat, long, alt = parse_iso_coordinates("+46.575707+14.395198+740")
    assert lat == 46.575707


def test_parse_iso_coor_no_alt_success():
    lat, long, alt = parse_iso_coordinates("+46.575707+14.395198")
    assert alt is None


def test_parse_iso_coor_fail():
    with pytest.raises(ValueError):
        parse_iso_coordinates("+4asdfasdasda8")


def test_parse_date_success():
    date = parse_date("2026-05-02T12:00:00Z")
    assert str(date) == "2026-05-02 12:00:00"


def test_parse_date_none_fail():
    with pytest.raises(ValueError):
        parse_date(None)


def test_parse_date_format_fail():
    with pytest.raises(ValueError):
        parse_date("2026-05-02T12asfasdfasdfasd:00:00Z")


def test_parse_label_success():
    label = parse_label("moor - A wetland found in")
    assert label == "moor"


def test_parse_label_none_fail():
    with pytest.raises(ValueError):
        parse_label(None)
