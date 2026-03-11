from enum import Enum


class NodeType(str, Enum):
    LLM = "llm"
    CODE = "code"
    KNOWLEDGE = "knowledge"
    API = "api"
