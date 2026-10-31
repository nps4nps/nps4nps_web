from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.core.celery_app import celery
from app.core.templates import templates
from app.services.tasks import heavy_add

router = APIRouter(prefix="/vis", tags=["views"])


@router.get("/sample-map", include_in_schema=False, response_class=HTMLResponse)
async def sample_map(request: Request):
    return templates.TemplateResponse(request=request, name="sample_map.html")


@router.post("/sample-map/query")
async def query_sample_map(request: Request):
    pass


# TODO (MMZ): route to get params and post-request; read from URL into pydantic schema
# TODO (MMZ): run as a celery registered task
# TODO(MMZ): route to receive post request and start of job, sends a waiting html+js site


@router.get("/sample-map/{task_id}")
async def get_sample_map(request: Request):
    pass


# TODO(MMZ): polling route for websocket and request redirect/send map


@router.get("/add")
async def add_numbers(x: int, y: int):
    task = heavy_add.delay(x, y)
    return {"task_id": task.id, "status": "queued"}


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    result = celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
