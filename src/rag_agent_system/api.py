from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from rag_agent_system.agents.factory import build_agent
from rag_agent_system.config import load_config
from rag_agent_system.agents.prompts import build_agent_prompt
from pydantic import BaseModel, field_validator
from threading import Lock
import logging
from time import perf_counter
from uuid import uuid4
from rag_agent_system.logging_config import configure_logging
from rag_agent_system.datasets import DatasetName, get_dataset_config_path
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config("configs/chunking_v2.yaml")
    configure_logging(config.log_level)
    app.state.agent_lock = Lock()
    app.state.agents= {}
    yield
class QueryRequest(BaseModel):
    question: str
    dataset: DatasetName="tinystories"
    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value=value.strip()
        if not value:
            raise ValueError("question cannot be empty")
        return value
app = FastAPI(lifespan=lifespan)
@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/query")
def query(payload: QueryRequest,request: Request):
    request_id=uuid4().hex
    start = perf_counter()
    with request.app.state.agent_lock:
        dataset = payload.dataset
        agents = request.app.state.agents

        if dataset not in agents:
            config = load_config(get_dataset_config_path(dataset))
            agents[dataset] = build_agent(config, dataset=dataset)

        agent = agents[dataset]
        prompt = build_agent_prompt(payload.question, dataset=dataset)
        result = agent.run(prompt)
        end = perf_counter()

    elapsed_seconds = end - start
    logger.info(
        "request_id=%s dataset=%s status=%s elapsed_seconds=%.3f",
        request_id,
        dataset,
        result["status"],
        elapsed_seconds,
    )
    return result
