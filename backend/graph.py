"""
LangGraph conversational agent for clinical trial discovery.
Multi-turn interviewer that collects: Type, Stage, Treatments, Location.
Supports natural conversation, general questions, and state persistence.
"""
from typing import List, Optional, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from schema import SearchFilters, MapboxOutput, SuggestionItem, SuggestionList
from trial_search import search_trials

# ── Constants ────────────────────────────────────────────────────────────────

DISCLAIMER = (
    "\n\n*Disclaimer: This chatbot provides information about clinical "
    "trials and is not a substitute for professional medical advice.*"
)

GUARDRAIL_TEXT = (
    "I'm designed to help patients explore cancer clinical trials. "
    "Please ask questions related to clinical trials."
)

# ── LLM Setup ────────────────────────────────────────────────────────────────

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
structured_llm = llm.with_structured_output(SearchFilters)
structured_suggestions = llm.with_structured_output(SuggestionList)

SYSTEM_PROMPT = (
    "You are an AI assistant helping cancer patients find clinical trials. "
    "Your goal is to extract clinical information from the user's message into the correct fields: "
    "- 'cancer_type': The disease (e.g., Breast Cancer, Lung Cancer). "
    "- 'cancer_stage': The numerical or descriptive stage (e.g., Stage 4, Stage IV). "
    "- 'prior_treatments': Procedures or drugs received (e.g., Chemotherapy, Surgery, Radiation). "
    "- 'location': City or province (e.g., Toronto, Ontario). "
    "\n\nCRITICAL: If the user provides clinical data or a location, EXTRACT it. "
    "\n\nRULE: 'Chemotherapy' and 'Surgery' are TREATMENTS, not cancer types."
    "\n\nRULE: If the user message is about cancer or trials (even if just a single word like 'Surgery'), DO NOT set 'is_off_topic' to true."
)


# ── Graph State ──────────────────────────────────────────────────────────────

class GraphState(TypedDict):
    user_message: str
    cancer_type: Optional[str]
    cancer_stage: Optional[str]
    prior_treatments: Optional[str]
    location: Optional[str]
    response_text: str
    suggestions: List[dict]   # list of {"label": str, "value": val}
    is_off_topic: bool
    is_question: bool         # True if the user asked a general question
    general_answer: Optional[str] # Answer to the general question


# ── Helpers ───────────────────────────────────────────────────────────────────

import re

# Question-word patterns (handles typos like "whats", "wat", "wht")
_QUESTION_STARTERS = re.compile(
    r"^(what|whats|wat|wht|how|why|when|where|who|which|"
    r"is\s|are\s|can\s|could\s|should\s|does\s|do\s|will\s|"
    r"tell\s+me|explain|describe)",
    re.IGNORECASE
)

# Known single-word DATA values that should never be treated as questions
_KNOWN_DATA_VALUES = {
    "surgery", "chemotherapy", "chemo", "radiation", "immunotherapy",
    "none", "breast", "lung", "colon", "melanoma", "leukemia", "prostate",
    "toronto", "montreal", "vancouver", "ottawa", "ontario", "quebec",
    "alberta", "calgary", "edmonton", "winnipeg", "halifax",
}


def _is_question_heuristic(text: str) -> bool:
    """Fast, deterministic check for question intent."""
    stripped = text.strip()
    words = stripped.split()

    # Single-word answers are almost always DATA (clicked a suggestion chip)
    if len(words) == 1:
        return False

    # Contains a question mark → it's a question
    if "?" in stripped:
        return True

    # Starts with a question word / phrase
    if _QUESTION_STARTERS.match(stripped):
        return True

    return False


# ── Nodes ────────────────────────────────────────────────────────────────────

def process_message(state: GraphState) -> dict:
    """Classify intent and extract info."""
    user_msg = state["user_message"]
    user_lower = user_msg.lower().strip()

    # 1. Classify intent — heuristic first, LLM fallback only if ambiguous
    is_question = _is_question_heuristic(user_lower)

    # For multi-word messages that the heuristic didn't catch,
    # fall back to LLM classification only if there are 2+ words
    if not is_question and len(user_lower.split()) > 2:
        classification_prompt = [
            SystemMessage(content=(
                "Classify if the user's intent is 'asking a question' (e.g. 'What is immunotherapy?') "
                "or 'providing personal data/confirmation' (e.g. 'I have breast cancer', 'Stage 3'). "
                "Return only 'QUESTION' or 'DATA'."
            )),
            HumanMessage(content=user_msg)
        ]
        intent_resp = llm.invoke(classification_prompt).content.strip().upper()
        is_question = "QUESTION" in intent_resp

    updates = {"is_question": is_question, "general_answer": None}
    
    # 2. Extract clinical info (always extract for field mapping)
    prompt_messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ]
    
    try:
        filters = structured_llm.invoke(prompt_messages)
        updates["is_off_topic"] = filters.is_off_topic
        
        # Override: if it's a question, it's NOT off-topic (the LLM sometimes
        # marks questions like "whats chemo" as off-topic)
        if is_question:
            updates["is_off_topic"] = False
        
        # Check for explicit "None" or similar in treatments
        if ("none" in user_lower or "no treatments" in user_lower) and not is_question:
             if state.get("cancer_stage") and not state.get("prior_treatments"):
                updates["prior_treatments"] = "None"
        
        # Map LLM extractions to profile fields
        # CRITICAL: If it's a question, do NOT update clinical fields.
        # The user is asking about a concept, not providing their own data.
        fields = ["cancer_type", "cancer_stage", "prior_treatments"]
        if not is_question:
            for field in fields:
                val = getattr(filters, field, None)
                if val and val.lower() not in ["none", "unknown", "null"]:
                    updates[field] = val
        
        # Location is safe to update even during questions (e.g. "What trials are in Toronto?")
        loc = getattr(filters, "location", None)
        if loc and loc.lower() not in ["none", "unknown", "null"]:
            updates["location"] = loc
                    
    except Exception:
        updates["is_off_topic"] = False

    return updates


def handle_question(state: GraphState) -> dict:
    """Answer general questions as a real person."""
    prompt = [
        SystemMessage(content=(
            "You are a helpful and polite conversational clinical trial assistant. "
            "Answer the user's question briefly and accurately. "
            "If they just updated their location or info, acknowledge it. "
            "Then politely steer them back to completing their profile if needed."
        )),
        HumanMessage(content=state["user_message"])
    ]
    answer = llm.invoke(prompt).content
    return {"general_answer": answer}


def generate_ai_suggestions(state: GraphState) -> dict:
    """Generate the next interview step/question."""
    # Determine missing field
    if not state.get("cancer_type"):
        question = "To help you find the right trials, what type of cancer are you looking for?"
        context = "Suggest common cancers like Breast, Lung, Leukemia, Melanoma."
    elif not state.get("cancer_stage"):
        question = f"Got it. What is the **stage** of your {state['cancer_type']}?"
        context = "Suggest stages like Stage I, II, III, IV, or Recurrent."
    elif not state.get("prior_treatments"):
        question = "Understood. Have you had any **prior treatments** like chemotherapy or surgery?"
        context = "Suggest Surgery, Chemotherapy, Radiation, or None."
    elif not state.get("location"):
        question = "Finally, **where are you located** (City or Province)?"
        context = "Suggest major Canadian cities like Toronto, Montreal, Vancouver."
    else:
        # If all data is present but we are here, it might be a question follow-up
        return {"response_text": state.get("general_answer", "Searching..."), "suggestions": []}

    # If we just answered a question, prepend the answer
    final_text = question
    if state.get("general_answer"):
        final_text = f"{state['general_answer']}\n\n---\n{question}"

    # Generate Chips
    prompt = [
        SystemMessage(content=f"Generate 3-4 clickable suggestion chips for: {context}"),
        HumanMessage(content=f"Current Question: {question}")
    ]
    try:
        ai_suggs = structured_suggestions.invoke(prompt)
        suggestions = [{"label": s.label, "value": s.value} for s in ai_suggs.suggestions]
    except:
        suggestions = []

    return {
        "response_text": final_text,
        "suggestions": suggestions,
    }


def search_database(state: GraphState) -> dict:
    """Perform search."""
    filters = SearchFilters(
        cancer_type=state.get("cancer_type"),
        cancer_stage=state.get("cancer_stage"),
        prior_treatments=state.get("prior_treatments"),
        location=state.get("location"),
    )
    mapbox_output = search_trials(filters)
    
    prefix = ""
    if state.get("general_answer"):
        prefix = f"{state['general_answer']}\n\n---\n"

    if not mapbox_output.trials:
        response_text = (
            f"{prefix}No trials found for **{filters.cancer_type}** ({filters.cancer_stage}) "
            f"near **{filters.location}**. Try a different city?"
            + DISCLAIMER
        )
    else:
        json_result = mapbox_output.model_dump_json(indent=2)
        response_text = (
            f"{prefix}I found trials for **{filters.cancer_type}** near **{filters.location}**:\n\n"
            f"```json\n{json_result}\n```"
            + DISCLAIMER
        )
    
    return {"response_text": response_text, "suggestions": []}


def handle_off_topic(state: GraphState) -> dict:
    return {"response_text": GUARDRAIL_TEXT, "suggestions": []}


# ── Routing ──────────────────────────────────────────────────────────────────

def route_after_processing(state: GraphState) -> str:
    if state.get("is_off_topic"):
        return "off_topic"
    
    # Check if all 4 are present - if so, ALWAYS search even if it was a question
    # (e.g., "What trials are in Montreal?" should search Montreal if cancer info is already known)
    if (state.get("cancer_type") and state.get("cancer_stage") and 
        state.get("prior_treatments") and state.get("location")):
        return "ready_to_search"
    
    if state.get("is_question"):
        return "is_question"
    
    return "generate_suggestions"


# ── Build Graph ──────────────────────────────────────────────────────────────

workflow = StateGraph(GraphState)

workflow.add_node("process_message", process_message)
workflow.add_node("handle_question", handle_question)
workflow.add_node("generate_ai_suggestions", generate_ai_suggestions)
workflow.add_node("search_database", search_database)
workflow.add_node("handle_off_topic", handle_off_topic)

workflow.set_entry_point("process_message")

workflow.add_conditional_edges(
    "process_message",
    route_after_processing,
    {
        "off_topic": "handle_off_topic",
        "is_question": "handle_question",
        "generate_suggestions": "generate_ai_suggestions",
        "ready_to_search": "search_database",
    },
)

workflow.add_edge("handle_question", "generate_ai_suggestions")
workflow.add_edge("generate_ai_suggestions", END)
workflow.add_edge("search_database", END)
workflow.add_edge("handle_off_topic", END)

app_graph = workflow.compile()
