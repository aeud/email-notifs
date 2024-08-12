import json
import base64
from flask import Flask, request
from jinja2 import Environment, PackageLoader, select_autoescape
import requests
import logging

import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

app = Flask(__name__)


env = Environment(
    loader=PackageLoader("emails", "templates"),
    autoescape=select_autoescape()
)


MAILGUN_API_URL = "https://api.mailgun.net/v3/eudes.co/messages"
FROM_EMAIL_ADDRESS = "bot@eudes.co"


def send_single_email(to_address, subject, message, html, debug=False):
    if debug:
        with open("./output.html", "w") as file:
            file.write(html)
            file.close()
            return
    try:
        api_key = os.getenv("MAILGUN_API_KEY")
        resp = requests.post(
            MAILGUN_API_URL,
            auth=("api", api_key),
            data={
                "from": FROM_EMAIL_ADDRESS,
                "to": to_address,
                "subject": subject,
                "text": message,
                "html": html,
            },
            # verify=False,
        )
        if resp.status_code == 200:
            logging.info(f"Successfully sent an email to '{to_address}' via Mailgun API.")
        else:
            logging.error(f"Could not send the email, reason: {resp.text}")

    except Exception as ex:
        logging.exception(f"Mailgun error: {ex}")

# def main():
#     message = "Testing Mailgun API for a single email"
#     subject = "🆘 Oops, something went wrong"
#     to = "adrien.eudes@gmail.com"
#     template = env.get_template("main.html")
#     html = template.render(message=message, subject=subject)
#     send_single_email(to, subject, message, html, debug=False)

@app.route("/", methods=["POST"])
def index():
    """Receive and parse Pub/Sub messages."""
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        text_payload = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()
        payload = json.loads(text_payload)
        message = payload.get("message", "N/A")
        subject = payload.get("subject", "N/A")
        cta_link = payload.get("cta_link", None)
        to = payload.get("to", "N/A")
        template = env.get_template("main.html")
        html = template.render(message=message, subject=subject, cta_link=cta_link)
        send_single_email(to, subject, message, html, debug=False)

    return ("", 204)

# if __name__ == "__main__":
#     main()
    
    