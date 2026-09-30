"""
Skeleton LangGraph pipeline - this is the "smallest possible end-to-end
skeleton" from the roadmap: one hardcoded input -> one LLM call ->
one policy check -> a stub approval -> a stub DB insert.

Get this running before building out real agents. Once it works,
each function below gets replaced by a real agent (extraction, OCR,
catalog lookup, etc.) without changing the graph shape.

Run with: python agents/graph.py
"""
import os
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()


class CaseState(TypedDict):
    raw_input: str
    extracted: dict
    policy_status: str
    approved: bool


def classify_and_extract(state: CaseState) -> CaseState:
    """
    Stub for the Intent & Classification + Extraction/Planning agents.
    Replace with a real Gemini/Groq call once GEMINI_API_KEY is set.
    """
    # TODO: call the LLM here, e.g.:
    # import google.generativeai as genai
    # genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    # model = genai.GenerativeModel("gemini-1.5-flash")
    # response = model.generate_content(f"Extract fields as JSON from: {state['raw_input']}")
    state["extracted"] = {"item": "laptop", "quantity": 5, "price": 290000}
    return state


def check_policy(state: CaseState) -> CaseState:
    """Stub for the Policy & Business Rule Agent - reads rules from data, not code."""
    rules = {"cfo_approval_threshold": 50000}
    if state["extracted"].get("price", 0) > rules["cfo_approval_threshold"]:
        state["policy_status"] = "needs_cfo_approval"
    else:
        state["policy_status"] = "ok"
    return state


def human_approval(state: CaseState) -> CaseState:
    """Stub for the Human Approval Dashboard - just auto-approves for now."""
    print(f"[APPROVAL NEEDED] {state['extracted']} -> {state['policy_status']}")
    state["approved"] = True  # replace with a real UI/DB-backed approval flow
    return state


def execute(state: CaseState) -> CaseState:
    """Stub for the Database/Execution Agent."""
    if state["approved"]:
        print(f"[DB INSERT] {state['extracted']}")
    return state


def run_skeleton(raw_input: str):
    """Runs the pipeline linearly - swap for a real langgraph.StateGraph once each
    stage is doing real work and you need branching (doc path vs request path)."""
    state: CaseState = {"raw_input": raw_input, "extracted": {}, "policy_status": "", "approved": False}
    state = classify_and_extract(state)
    state = check_policy(state)
    state = human_approval(state)
    state = execute(state)
    return state


if __name__ == "__main__":
    result = run_skeleton("5 laptops for new interns")
    print("Final state:", result)
