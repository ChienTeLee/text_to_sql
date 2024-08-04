import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import create_document_store, create_rag_pipeline, run_rag_pipeline


class Question(BaseModel):
    user: str
    timestamp: str
    query: str


app = FastAPI()

# # CORS configuration
# origins = [
#     "http://localhost/",  # Your Vue.js frontend URL
#     "http://127.0.0.1/",
#     "http://192.168.0.104/"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["DELETE", "GET", "POST", "PUT"],
#     allow_headers=["*"],
#     expose_headers=["*"],
# )

# build llm
os.environ["OPENAI_API_KEY"] = "your_openai_key"
file_path = "./table_schema.txt"
document_store = create_document_store(file_path)
rag_pipeline = create_rag_pipeline(document_store)


@app.post("/ask/")
async def ask_llm(question: Question):
    print(question)
    try:
        result = run_rag_pipeline(rag_pipeline, question.query)
        print(result)
        return {
            "user": "server",
            "timestamp": datetime.now(),
            "response": result,
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Bad request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)