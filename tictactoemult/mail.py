# Python file for sending mails
import resend
from .custom_settings import RESEND_API_KEY

def send_mail(receiver, subject, html):
    try:
        resend.api_key = RESEND_API_KEY

        params: resend.Emails.SendParams = {
            "from": "Tic Tac Toe Multiplayer <support@jakobjohannes.com>",
            "to": [receiver],
            "subject": subject,
            "html": html,
        }

        email = resend.Emails.send(params)
        return(email)
    except:
        return("error")