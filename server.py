import os
import httpx
from fastmcp import FastMCP

mcp = FastMCP("resend-email")

@mcp.tool()
async def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to the specified address via Resend."""
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise ValueError("RESEND_API_KEY environment variable is not set")

    from_address = os.environ.get("FROM_ADDRESS", "onboarding@resend.dev")

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_address,
                "to": [to],
                "subject": subject,
                "text": body,
            },
        )
        if response.status_code != 200:
            raise RuntimeError(f"Resend API error {response.status_code}: {response.text}")

        email_id = response.json().get("id", "unknown")
        return f"Email sent successfully. Resend ID: {email_id}"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
