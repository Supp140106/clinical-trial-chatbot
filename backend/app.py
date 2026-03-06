"""
Chainlit application — wires the LangGraph conversational agent to the UI.
Maintains a persistent patient profile in the session.
"""
import chainlit as cl
from graph import app_graph

# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_actions(suggestions: list[dict]) -> list[cl.Action]:
    """Convert graph suggestion dicts into Chainlit Action buttons."""
    actions = []
    for s in suggestions:
        actions.append(
            cl.Action(
                name="suggestion_click",
                payload={"query": s["value"]},
                label=s["label"],
                tooltip="Click to select",
            )
        )
    return actions


async def _run_graph(user_message: str):
    """Invoke the LangGraph with the current session profile."""
    profile = cl.user_session.get("profile", {})

    state = {
        "user_message": user_message,
        "cancer_type": profile.get("cancer_type"),
        "cancer_stage": profile.get("cancer_stage"),
        "prior_treatments": profile.get("prior_treatments"),
        "location": profile.get("location"),
        "response_text": "",
        "suggestions": [],
        "is_off_topic": False,
        "is_question": False,
        "general_answer": None,
    }

    try:
        result = app_graph.invoke(state)
    except Exception as e:
        await cl.Message(content=f"An error occurred: {str(e)}").send()
        return

    # Update profile (state persistence)
    # We always keep the values from the result if they exist
    for field in ["cancer_type", "cancer_stage", "prior_treatments", "location"]:
        if result.get(field):
            profile[field] = result[field]
    
    cl.user_session.set("profile", profile)

    # REMOVED: is_complete reset. We want it to be persistent!
    # If the user wants to reset, they can start a new chat.

    response_text = result.get("response_text", "")
    suggestions = result.get("suggestions", [])
    actions = _build_actions(suggestions) if suggestions else None

    # Final Message Send
    await cl.Message(content=response_text, actions=actions).send()


# ── Chainlit Callbacks ───────────────────────────────────────────────────────

@cl.on_chat_start
async def start():
    cl.user_session.set("profile", {})
    await cl.Message(
        content=(
            "👋 Welcome to the **Clinical Trial Finder**!\n\n"
            "I'm here to help you find trials and answer your questions. "
            "Tell me about your condition to get started."
        )
    ).send()


@cl.action_callback("suggestion_click")
async def on_action(action: cl.Action):
    """Handle clicks on AI-generated suggestion chips."""
    query = action.payload.get("query", "")
    await cl.Message(content=query, author="User").send()
    await _run_graph(query)


@cl.on_message
async def main(message: cl.Message):
    # Support "reset" command
    if message.content.lower().strip() == "/reset":
        cl.user_session.set("profile", {})
        await cl.Message(content="Profile reset! How can I help?").send()
        return

    await _run_graph(message.content)
