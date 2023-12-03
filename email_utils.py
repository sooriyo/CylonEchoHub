from flask_mail import Message
from app import mail, db  # Import the mail instance from app.py
from utils import generate_verification_token


def send_verification_email(user_to_verify):
    code = generate_verification_token()
    user_to_verify.email_verification_code = code
    db.session.commit()

    subject = 'CylonEchoPlug - Email Verification'
    body = f'Your verification code is: {code}'

    message = Message(subject, recipients=[user_to_verify.email], body=body)
    mail.send(message)
