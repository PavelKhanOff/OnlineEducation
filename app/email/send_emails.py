from app.config import EMAIL_URL_SEND_REGISTER_MAIL, VERIFICATION_URL
import httpx


async def send_register_mail(email, verify_token):
    url = EMAIL_URL_SEND_REGISTER_MAIL
    action_url = f"{VERIFICATION_URL}?token={verify_token}"
    data = {
        'email': email,
        "template_name": "test.html",
        "template_subject": "string",
        "template_body": {'action_url': action_url, "email": email},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, json=data, timeout=8)
        response.raise_for_status()

    return response.json()
