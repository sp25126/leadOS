"""
routers/chat.py
────────────────
Simple AI agent chat endpoint.
Returns strictly-typed { assistantMessage, actions[] } so the Next.js
frontend can execute UI commands without parsing free text.
"""
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/agent", tags=["AI Agent"])


# ── Request / Response ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class ChatAction(BaseModel):
    type:     str               # "NAVIGATE" | "API_CALL" | "TOAST"
    path:     str | None = None          # for NAVIGATE
    endpoint: str | None = None          # for API_CALL
    method:   str | None = None          # for API_CALL
    payload:  dict | None = None         # for API_CALL


class ChatResponse(BaseModel):
    assistantMessage: str
    actions:          list[ChatAction] = []


# ── Intent map ────────────────────────────────────────────────────────

_INTENTS: list[tuple[list[str], str, list[dict]]] = [
    (
        ["skip report", "junk", "filtered", "show report"],
        "Opening the Outreach Command Center — you can review the skip report there.",
        [{"type": "NAVIGATE", "path": "/outreach"}],
    ),
    (
        ["send email", "start send", "launch outreach", "run outreach", "live send"],
        "Queuing a live email send run. Calling the send endpoint now.",
        [{"type": "API_CALL", "endpoint": "/api/email/send-run-by-source", "method": "POST", "payload": {"dryrun": False}}],
    ),
    (
        ["dry run", "dry test", "test send", "preview send"],
        "Running a dry-run — no emails will actually be sent. Calling the endpoint.",
        [{"type": "API_CALL", "endpoint": "/api/email/send-run-by-source", "method": "POST", "payload": {"dryrun": True}}],
    ),
    (
        ["hunt leads", "search leads", "find leads", "discover"],
        "Navigating to the lead search page.",
        [{"type": "NAVIGATE", "path": "/"}],
    ),
    (
        ["history", "past searches", "previous sessions"],
        "Opening search history.",
        [{"type": "NAVIGATE", "path": "/history"}],
    ),
    (
        ["quota", "credits", "api usage", "rate limit"],
        "You can see live API credit usage in the Quota panel on the right side of the home page.",
        [],
    ),
]

_HELP_MESSAGE = (
    "I can help you with: **lead search**, **skip report**, **dry-run send**, **live send**, "
    "**history**, and **quota status**. Try: 'Show skip report' or 'Send emails'."
)


def _match_intent(message: str) -> tuple[str, list[dict]]:
    lower = message.lower()
    for keywords, reply, actions in _INTENTS:
        if any(kw in lower for kw in keywords):
            return reply, actions
    return _HELP_MESSAGE, []


# ── Endpoint ──────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def agent_chat(body: ChatRequest) -> ChatResponse:
    """
    Accept a plain-text message and return a structured response with
    an assistant message and zero or more executable UI actions.
    """
    if not body.message.strip():
        return ChatResponse(
            assistantMessage="Please send a message.",
            actions=[],
        )

    assistant_msg, raw_actions = _match_intent(body.message)

    actions = [ChatAction(**a) for a in raw_actions]

    return ChatResponse(
        assistantMessage=assistant_msg,
        actions=actions,
    )
