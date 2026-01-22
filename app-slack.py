import os
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from browser_use import Agent
from browseruse_runner import run_browseruse
import threading

# ----------------------------
# Slack App initialization
# ----------------------------
slack_app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)


def run_and_post(channel_id, topic, client):
    try:
        result = run_browseruse(topic)

        MAX_LEN = 3000
        chunks = [result[i:i+MAX_LEN] for i in range(0, len(result), MAX_LEN)]

        for chunk in chunks:
            client.chat_postMessage(
                channel=channel_id,
                text=chunk  # 🔥 NO blocks
            )

    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Error while fetching events:\n{str(e)}"
        )

@slack_app.command("/events")
def event_command(ack, respond, command, client):
    ack()

    topic = command["text"]
    channel_id = command["channel_id"]

    if not topic.strip():
        respond("❌ Please provide a topic. Example:\n`/event tech events in Dublin`")
        return

    respond("⏳ Searching for events across platforms…")

    # Run BrowserUse in background thread
    threading.Thread(
        target=run_and_post,
        args=(channel_id, topic, client),
        daemon=True
    ).start()


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    flask_app.run(port=3000)
