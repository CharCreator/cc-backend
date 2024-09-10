from ..config import Config
import aiohttp

config = Config()


async def send_custom_email(
    recipient: str,
    subject: str,
    plain_body: str,
    html_body: str = None,
):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config.mail_send_api}/send_email",
            json={
                "subject": subject,
                "plain_body": plain_body,
                "to": recipient,
                "html_body": html_body,
            },
            headers={"X-Auth-Token": config.mail_send_token},
        ) as resp:
            resp.raise_for_status()


async def send_signup_email(
    email: str,
    url: str,
):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config.mail_send_api}/send_signup_email",
            json={
                "email": email,
                "url": url,
            },
            headers={"X-Auth-Token": config.mail_send_token},
        ) as resp:
            resp.raise_for_status()


async def send_password_reset_email(
    email: str,
    url: str,
):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config.mail_send_api}/send_reset_password_email",
            json={
                "email": email,
                "url": url,
            },
            headers={"X-Auth-Token": config.mail_send_token},
        ) as resp:
            resp.raise_for_status()
