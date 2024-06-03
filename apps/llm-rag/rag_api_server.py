from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import pathlib
from rag_llama_index import get_rag_query_engine
from llama_index.core.base.base_query_engine import BaseQueryEngine


class QueryDocs(BaseModel):
    query: str


class RagPipeline:
    query_engine: BaseQueryEngine


app = FastAPI()
rag_pipeline = RagPipeline()


@app.get("/load_docs")
def load_docs():
    current_file_path = pathlib.Path(__file__).parent.resolve()
    rag_pipeline.query_engine = get_rag_query_engine(current_file_path)
    return {"messsage": "success"}


@app.post("/answer")
async def get_answer(query_docs: QueryDocs):
    answer = rag_pipeline.query_engine.query(query_docs.query)
    return {"result": answer.response}


if __name__ == "__main__":
    uvicorn.run(app, port=4444)
