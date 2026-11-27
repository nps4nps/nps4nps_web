import asyncio
import json
from typing import Annotated

from celery.result import AsyncResult
from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app.core.celery_app import celery
from app.core.config import settings
from app.core.templates import templates
from app.schemas.sample_mapping import SampleMapping
from app.tasks.sampling import sample_mapping

router = APIRouter(prefix="/sampling", tags=["views"])


@router.get("/default", include_in_schema=False, response_class=HTMLResponse)
async def get_default_map_sample(request: Request):
    """Re-draw sample map every n minutes"""
    dlft_json = settings.map_dir / f"{settings.dflt_sample_map_name}.json"

    if not dlft_json.exists():
        raise HTTPException(
            status_code=503,
            detail="Map is not available yet",
        )

    with open(dlft_json) as f:
        data = json.load(f)

    return templates.TemplateResponse(
        "sample-map-results.html",
        {
            "request": request,
            "data": data["last_updated"],
        },
    )


@router.get("/default/document")
async def default_sampling_document():
    """Retrieve the actual data to load into iFrame"""
    dlft_map = settings.map_dir / f"{settings.dflt_sample_map_name}.html"

    if not dlft_map.exists():
        raise HTTPException(
            status_code=404,
            detail="Map not available",
        )

    html = dlft_map.read_text(encoding="utf-8")

    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "no-store"},
    )


@router.get("/default/download")
async def default_sampling_download():
    csv_file = settings.map_dir / f"{settings.dflt_sample_map_name}.csv"

    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="CSV not available")

    return FileResponse(
        path=csv_file,
        media_type="text/csv",
        filename="default-map-data.csv",
    )


@router.get("/", include_in_schema=False, response_class=HTMLResponse)
async def get_map_sample(request: Request):
    """Route to allow for custom sampling map drawing"""
    # TODO(MMZ 26.11. allow modification of query)
    return templates.TemplateResponse(request=request, name="sample-map-get.html")


@router.post("/submit", include_in_schema=False, response_class=RedirectResponse)
async def submit_map_sample(p: Annotated[SampleMapping, Form()]):
    """Redirect to waiting page"""
    # TODO(MMZ 26.11. allow modification of query)
    task = sample_mapping.delay(p.query)
    return RedirectResponse(
        url=f"{router.prefix}/{task.id}/waiting",
        status_code=303,
    )


@router.get("/{job_id}/waiting", include_in_schema=False, response_class=HTMLResponse)
async def waiting_map_sample(request: Request, job_id: str):
    """Serves the waiting page for long-running jobs"""
    return templates.TemplateResponse(
        request=request,
        name="sample-map-waiting.html",
        context={
            "job_id": job_id,
        },
    )


@router.websocket("/ws/jobs/{job_id}")
async def job_websocket(websocket: WebSocket, job_id: str):
    """Allows polling for long-running jobs"""
    await websocket.accept()
    try:
        task = AsyncResult(job_id, app=celery)

        while True:
            state = await asyncio.to_thread(
                lambda: {"state": task.state, "info": task.info}
            )

            await websocket.send_json(state)

            if state["state"] in ("SUCCESS", "FAILURE", "REVOKED"):
                break

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass


@router.get("/{job_id}/results")
async def job_results(request: Request, job_id: str):
    """Serve the sampling map if job is ready"""
    task = AsyncResult(job_id, app=celery)

    if task.state != "SUCCESS":
        raise HTTPException(
            status_code=409,
            detail="Map is not ready yet",
        )
    return templates.TemplateResponse(
        "sample-map-results.html",
        {
            "request": request,
            "job_id": task.id,
        },
    )


@router.get("/{job_id}/document")
async def sampling_document(job_id: str):
    """Retrieve the actual data to load into iFrame"""
    task = AsyncResult(job_id, app=celery)

    if task.state != "SUCCESS":
        raise HTTPException(404, "Map not available")

    return HTMLResponse(content=task.result["html"])


@router.get("/{job_id}/download")
async def sampling_download(job_id: str):
    task_result = AsyncResult(job_id, app=celery)

    if not task_result.ready():
        raise HTTPException(
            status_code=409,
            detail="Sampling data collection not finished.",
        )

    if task_result.failed():
        raise HTTPException(
            status_code=500,
            detail="Sampling data collection not failed.",
        )

    result = task_result.result

    return Response(
        content=result["csv"],
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="sampling-{job_id}.csv"'
        },
    )
