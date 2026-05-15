import os
import httpx
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("resend-email")

@mcp.tool()
async def send_email(to: str, subject: str, body: str, html: str | None = None) -> str:
    """Send an email via Resend. Provide html for a formatted email; body is the plain-text fallback."""
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise ValueError("RESEND_API_KEY environment variable is not set")

    from_address = os.environ.get("FROM_ADDRESS", "onboarding@resend.dev")

    payload: dict = {
        "from": from_address,
        "to": [to],
        "subject": subject,
        "text": body,
    }
    if html:
        payload["html"] = html

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Resend API error {response.status_code}: {response.text}")

        email_id = response.json().get("id", "unknown")
        return f"Email sent successfully. Resend ID: {email_id}"


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
