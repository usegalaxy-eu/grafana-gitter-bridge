import os
import yaml
import requests
from flask import Flask, request, abort, jsonify
import json

app = Flask(__name__)

default_path = os.path.join(app.root_path, "config.yaml")
with open(os.environ.get("CONFIG_PATH", default_path), "r") as f:
    c = yaml.safe_load(f)
    for key in c.keys():
        app.config[key] = c[key]


def parse(request):
    j = request.get_json()

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer %s" % app.config["gitter_token"],
    }
    msg = "**[%s](%s)**\n\n" % (j["title"], j.get("ruleUrl", ""))

    if "evalMatches" in j:
        for metric in j["evalMatches"]:
            msg += "%s - %s\n\n" % (metric["metric"], metric["value"])

    if "imageUrl" in j:
        msg += "![](%s)" % j["imageUrl"]

    requests.post(
        "https://api.gitter.im/v1/rooms/%s/chatMessages" % app.config["room_id"],
        data=json.dumps({"text": msg}),
        headers=headers,
    )


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        verify_token = request.args.get("verify_token")
        if verify_token != app.config["token"]:
            return jsonify({"status": "bad token"}), 401

        parse(request)
        return jsonify({"status": "success"}), 200
    else:
        abort(400)
