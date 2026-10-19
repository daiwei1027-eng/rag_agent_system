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
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config("configs/chunking_v2.yaml")
    configure_logging(config.log_level)
    agent = build_agent(config)
    app.state.agent_lock = Lock()
    app.state.agent=agent
    yield
class QueryRequest(BaseModel):
    question: str
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
        agent = request.app.state.agent
        prompt = build_agent_prompt(payload.question)
        result = agent.run(prompt)
        end = perf_counter()

    elapsed_seconds = end - start
    logger.info(
        "request_id=%s status=%s elapsed_seconds=%.3f",
        request_id,
        result["status"],
        elapsed_seconds,
    )
    return result