from flask import Flask, request, jsonify
from generate_app import create_app
from push_to_github import create_repo
from notify_evaluation import notify_evaluation
from save_attachments import save_attachments
from round2_handler import handle_round2
from dotenv import load_dotenv
import os

load_dotenv()
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

VALID_SECRETS = {"24f1002781@ds.study.iitm.ac.in": "my_shared_secret123"}

TASK_TIMESTAMPS = {}

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "App is running!"

@app.route("/api-endpoint", methods=["POST"])
def receive_request():
    data = request.get_json()
    print("Received request:", data)
    email = data.get("email")
    provided_secret = data.get("secret")
    if email not in VALID_SECRETS or VALID_SECRETS[email] != provided_secret:
        return jsonify({"error": "Invalid secret"}), 403

    # Save attachments for LLM and app use
    attachments = data.get("attachments", [])
    save_attachments(attachments)
    brief = data.get("brief", "Hello World")
    checks = data.get("checks", [])
    nonce = data.get("nonce")
    print(f"Verified nonce for {email}: {nonce}")

    round_number = data.get("round", 1)
    task_name = data.get("task", "default-task")

    if round_number == 1:
        create_app(brief, attachments)
        repo_url, pages_url, commit_sha = create_repo(task_name, brief, checks)
        # Store IITM's timestamp if present, else parse from repo
        TASK_TIMESTAMPS[task_name] = data.get("timestamp", repo_url.split('-')[-1].replace('.git', ''))
    elif round_number == 2:
        data['timestamp'] = TASK_TIMESTAMPS.get(task_name)
        if not data['timestamp']:
            return jsonify({"error": "No Round 1 timestamp found for this task"}), 400
        repo_url, pages_url, commit_sha = handle_round2(data)
    else:
        return jsonify({"error": "Invalid round"}), 400

    notify_payload = {
        "email": email,
        "task": task_name,
        "round": round_number,
        "nonce": nonce,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }
    notify_evaluation(data.get("evaluation_url"), notify_payload)
    return jsonify({"usercode": "student123"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)

