import os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import (
    create_document_store,
    create_rag_pipeline,
    run_rag_pipeline,
    get_sqlite_result,
)


class Question(BaseModel):
    user: str
    timestamp: str
    query: str


app = FastAPI()


# CORS configuration
origins = [
    "http://localhost:8080/ ",  # Your Vue.js frontend URL
    "http://192.168.0.104:8080/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# build document store and RAG
os.environ["OPENAI_API_KEY"] = "your_openai_api"
document_file_lst = list(Path("./documents").glob("*.txt"))
document_store = create_document_store(document_file_lst)
rag_pipeline = create_rag_pipeline(document_store)
rag_pipeline.warm_up()

@app.post("/ask_llm/")
async def ask_llm(question: Question):
    # run llm
    print(question)
    rag_result, _ = run_rag_pipeline(rag_pipeline, question.query)
    print(rag_result)
    db_id = rag_result["db_id"]
    query = rag_result["query"]

    # run sqlite
    sqlite_result = get_sqlite_result(db_id, query)

    return {
        "user": "server",
        "timestamp": datetime.now(),
        "db_id": db_id,
        "response": query,
        "sqlite_result": sqlite_result,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)