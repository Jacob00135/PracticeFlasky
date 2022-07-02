from flask import render_template
from flask_mail import Message
from config import Config
from . import mail


def send_email(to, subject, template, **kwargs):
    msg = Message(
        Config.FLASKY_MAIL_SUBJECT_PREFIX + subject,
        sender=Config.FLASKY_MAIL_SENDER,
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
