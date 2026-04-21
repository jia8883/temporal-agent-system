from fastapi import FastAPI
from temporalio.client import Client
from pydantic import BaseModel, Field

from api.workflows.job_workflow import JobWorkflow
from api.utils.temporal_client import get_temporal_client
from api.utils.temporal_ready import wait_for_temporal_ready

from api.workflows.agent_workflow import AgentWorkflow
import uuid
from datetime import timedelta
from api.utils.prompt_loader import load_prompt


app = FastAPI()

client: Client = None
JOB_WORKFLOW_ID = "job-workflow"
JOB_TASK_QUEUE = "job-task-queue"
AGENT_TASK_QUEUE = "agent-task-queue"


@app.on_event("startup")
async def startup():
    global client
    client = await get_temporal_client()

    await wait_for_temporal_ready(client)

    print("FastAPI connected to Temporal")

    # Start workflow if not already running
    try:
        await client.start_workflow(
            JobWorkflow.run,
            id=JOB_WORKFLOW_ID,
            task_queue=JOB_TASK_QUEUE,
        )
        print("Workflow started")
    except Exception:
        print("Workflow already exists")


class JobRequest(BaseModel):
    title: str
    count: int = Field(..., ge=1, le=1000)

@app.post("/jobs")
async def add_job(req: JobRequest):
    handle = client.get_workflow_handle(JOB_WORKFLOW_ID)
    await handle.signal("add_request", {
        "title": req.title,
        "count": req.count
    })
    return {"message": "queued"}


@app.post("/jobs/pause")
async def pause():
    handle = client.get_workflow_handle(JOB_WORKFLOW_ID)

    status = await handle.query("get_status")

    if status == "paused":
        return {"error": "already paused"}

    await handle.signal("pause")
    return {"message": "paused"}


@app.post("/jobs/resume")
async def resume():
    handle = client.get_workflow_handle(JOB_WORKFLOW_ID)

    status = await handle.query("get_status")

    if status != "paused":
        return {"error": "not paused"}

    await handle.signal("resume")
    return {"message": "resumed"}


@app.get("/jobs/status")
async def status():
    handle = client.get_workflow_handle(JOB_WORKFLOW_ID)
    result = await handle.query("get_status")
    return {"status": result}


@app.post("/jobs/discard")
async def discard():
    handle = client.get_workflow_handle(JOB_WORKFLOW_ID)

    # Remove pending requests only
    await handle.signal("discard")
    
    return {"message": "discarded"}


class CrawlerRequest(BaseModel):
    input: str


@app.post("/agents/crawler")
async def crawler(req: CrawlerRequest):
    workflow_id = f"agent-{uuid.uuid4()}"

    prompt = load_prompt("agent_system")

    try:
        result = await client.execute_workflow(
            AgentWorkflow.run,
            {
                "input": req.input,
                "system_prompt": prompt
            },
            id=workflow_id,
            task_queue=AGENT_TASK_QUEUE,
            execution_timeout=timedelta(minutes=15),
        )

        return {"result": result}

    except Exception as e:
        return {"error": str(e)}
