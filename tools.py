import os
import requests
from strands import tool

MAILGUN_DOMAIN = "bys.digital"
EMAIL_TO = "skwltg90@naver.com"


def _send_email(subject: str, body: str):
    api_key = os.getenv("MAILGUN_API_KEY")
    requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", api_key),
        data={
            "from": f"Career Chatbot <postmaster@{MAILGUN_DOMAIN}>",
            "to": EMAIL_TO,
            "subject": subject,
            "text": body,
        },
        timeout=10,
    )


@tool
def record_user_details(email: str, name: str = "Name not provided", notes: str = "not provided") -> dict:
    """
    Record that a user is interested in being in touch and provided an email address.

    Args:
        email: The email address of this user
        name: The user's name, if they provided it
        notes: Any additional information about the conversation
    """
    _send_email(
        subject=f"[Career Chatbot] New contact: {name}",
        body=f"Name: {name}\nEmail: {email}\nNotes: {notes}",
    )
    return {"recorded": "ok"}


@tool
def record_unknown_question(question: str) -> dict:
    """
    Always use this tool to record any question that couldn't be answered.

    Args:
        question: The question that couldn't be answered
    """
    _send_email(
        subject="[Career Chatbot] Unknown question",
        body=f"Question: {question}",
    )
    return {"recorded": "ok"}
