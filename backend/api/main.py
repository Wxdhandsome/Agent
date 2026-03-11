from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator import CodeGenerator

app = FastAPI(title="LangFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

code_generator = CodeGenerator()


class GraphData(BaseModel):
    state: Dict[str, Any]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    workflowConfig: Dict[str, Any] = {}


@app.get("/")
async def root():
    return {"message": "LangFlow API is running"}


@app.post("/api/generate")
async def generate_code(graph_data: GraphData):
    try:
        data = graph_data.model_dump()
        code = code_generator.generate(
            {
                "state": data.get("state"),
                "nodes": data.get("nodes"),
                "edges": data.get("edges"),
            },
            data.get("workflowConfig")
        )
        return {"success": True, "code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
