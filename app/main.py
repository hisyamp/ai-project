from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.schemas import AskRequest, AskResponse, HealthResponse
from app.services import ingest
from app.services.rag import answer_question


@asynccontextmanager
async def lifespan(app: FastAPI):
    ingest.build_or_load_index()
    yield


app = FastAPI(
    title="NusantaraCare Internal Assistant API",
    description="RAG backend service untuk menjawab pertanyaan berdasarkan Panduan Operasional Internal NusantaraCare.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    return answer_question(request.question)
