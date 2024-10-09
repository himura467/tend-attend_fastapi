import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from pydantic.networks import EmailStr

from ta_core.error.error_code import ErrorCode


async def send_verification_email_async(
    host_email: EmailStr, verification_link: str
) -> tuple[int, ...]:
    sender_email = os.environ.get("GMAIL_SENDER_EMAIL")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if sender_email is None or app_password is None:
        return (ErrorCode.ENVIRONMENT_VARIABLE_NOT_SET,)

    message = MIMEMultipart("alternative")
    message["Subject"] = "[No-Reply] Email Verification"
    message["From"] = sender_email
    message["To"] = host_email

    text = f"Click the link below to verify your email address.\n{verification_link}"
    html = f'<html><body><a href="{verification_link}">Click here to verify your email address.</a></body></html>'

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        async with aiosmtplib.SMTP(
            hostname="smtp.gmail.com", port=465, use_tls=True
        ) as smtp:
            print(sender_email, app_password)
            await smtp.login(sender_email, app_password)
            await smtp.send_message(message)
        return ()
    except aiosmtplib.SMTPResponseException:
        return (ErrorCode.SMTP_ERROR,)
