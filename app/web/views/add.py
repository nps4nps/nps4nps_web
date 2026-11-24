# TODO(MMZ 24.11.26): remove for production; only proof of concept code

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
from app.schemas.add import AddModel
from app.tasks.add import heavy_add

router = APIRouter(prefix="/add", tags=["views"])


@router.get("/add", include_in_schema=False, response_class=HTMLResponse)
async def add_numbers(request: Request):
    return templates.TemplateResponse(request=request, name="add.html")


@router.post("/add/submit", include_in_schema=False, response_class=RedirectResponse)
async def add_numbers_submit(p: Annotated[AddModel, Form()]):
    task = heavy_add.delay(p.x, p.y)
    return RedirectResponse(
        url=f"{router.prefix}/add/{task.id}/waiting",
        status_code=303,
    )


@router.get(
    "/add/{job_id}/waiting", include_in_schema=False, response_class=HTMLResponse
)
async def waiting_page(request: Request, job_id: str):
    return templates.TemplateResponse(
        request=request,
        name="add-waiting.html",
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


@router.get("/jobs/{job_id}/results")
async def job_results(request: Request, job_id: str):
    task = AsyncResult(job_id, app=celery)

    if task.state != "SUCCESS":
        raise HTTPException(
            status_code=404,
            detail="Results are not available",
        )
    return templates.TemplateResponse(
        "add-results.html",
        {
            "request": request,
            "result": task.result,
        },
    )
