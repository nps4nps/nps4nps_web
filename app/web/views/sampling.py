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

router = APIRouter(prefix="/sampling", tags=["views"])


@router.get("/sample-map", include_in_schema=False, response_class=HTMLResponse)
async def sample_map(request: Request):
    pass


# TODO (MMZ): implement sample_map html with a post request


@router.post("/sample-map/query")
async def query_sample_map(request: Request):
    pass


# TODO (MMZ): route to get params and post-request; read from URL into pydantic schema
# TODO (MMZ): run as a celery registered task
# TODO(MMZ): route to receive post request and start of job, sends a waiting html+js site


@router.get("/sample-map/{task_id}")
async def get_sample_map(request: Request):
    pass


# TODO endpoint for websocket polling?
@router.get("/status/{task_id}")
async def get_status(task_id: str):
    result = celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
