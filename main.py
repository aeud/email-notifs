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

FROM_EMAIL_ADDRESS = os.getenv("FROM_EMAIL_ADDRESS")
MAILGUN_API_URL = os.getenv("MAILGUN_API_URL")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")

def send_single_email(to_address, subject, message, html, debug=False):
    if debug:
        with open("./output.html", "w") as file:
            file.write(html)
            file.close()
            return
    try:
        
        resp = requests.post(
            MAILGUN_API_URL,
            auth=("api", MAILGUN_API_KEY),
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
    