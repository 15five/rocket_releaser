import requests
import logging

logger = logging.getLogger(__name__)


def post_deployment_message_to_slack(slack_webhook_key, text):

    incoming_webhook_url = f"https://hooks.slack.com/services/{slack_webhook_key}"

    display_name = "Deployment Team"
    icon_emoji = ":rocket:"

    requests.post(
        incoming_webhook_url,
        json={
            "text": text,
            "username": display_name,
            "icon_emoji": icon_emoji,
        },
    )
