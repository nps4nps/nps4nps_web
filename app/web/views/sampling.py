import asyncio
from typing import Annotated

from celery.result import AsyncResult
from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.celery_app import celery
from app.core.templates import templates
from app.schemas.sample_mapping import SampleMapping
from app.tasks.sampling import sample_mapping

router = APIRouter(prefix="/sampling", tags=["views"])


@router.get("/", include_in_schema=False, response_class=HTMLResponse)
async def get_map_sample(request: Request):
    return templates.TemplateResponse(request=request, name="sample-map-get.html")


@router.post("/submit", include_in_schema=False, response_class=RedirectResponse)
async def submit_map_sample(p: Annotated[SampleMapping, Form()]):
    task = sample_mapping.delay(p.query)
    return RedirectResponse(
        url=f"{router.prefix}/{task.id}/waiting",
        status_code=303,
    )


@router.get("/{job_id}/waiting", include_in_schema=False, response_class=HTMLResponse)
async def waiting_map_sample(request: Request, job_id: str):
    return templates.TemplateResponse(
        request=request,
        name="sample-map-waiting.html",
        context={
            "job_id": job_id,
        },
    )


@router.websocket("/ws/jobs/{job_id}")
async def job_websocket(websocket: WebSocket, job_id: str):
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
    task = AsyncResult(job_id, app=celery)

    if task.state != "SUCCESS":
        raise HTTPException(404, "Map not available")

    return HTMLResponse(content=task.result)
