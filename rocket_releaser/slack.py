import slacker
import logging

logger = logging.getLogger(__name__)


def post_deployment_message_to_slack(slack_webhook_key, text):

    incoming_webhook_url = f"https://hooks.slack.com/services/{slack_webhook_key}"

    # We will continue to use Slacker for posting internal messages to webhooks.
    # There is no reason to switch to SlackClient. Alternatively, we could just use
    # the requests library directly.
    slack = slacker.Slacker("", incoming_webhook_url=incoming_webhook_url)

    display_name = "Deployment Team"
    icon_url = ":rocket:"

    slack.incomingwebhook.post(
        {
            "text": text,
            "username": display_name,
            "icon_url": icon_url,
            "icon_emoji": icon_url,
        }
    )
