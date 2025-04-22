import operator
from typing import TypedDict, Dict, Any, Annotated, Sequence, List
from langchain_core.messages import BaseMessage

class State(TypedDict):
    user_preferences : Dict[str, Any]
    agent_actions : Annotated[Sequence[BaseMessage], operator.add]
    raw_jobs : List[Dict]
    relevant_jobs : List[Dict]
    ranked_jobs : List[Dict]