from pymongo import MongoClient
from datetime import datetime, timezone
import json
import pytz
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
import os
import traceback
import requests

load_dotenv()

uri = os.getenv("MONGO_URL") # loading the database url from .env
notification_reciver = os.getenv("NOTIFICATION_RECIVER")

# connection to database
client = MongoClient(uri)
db = client["github-webhook"]
collection = db["webhook"]

# flask app
app = Flask(__name__)

# function to render the response send via github webhook
def parse_event(event_type, payload):
    print(f"[INFO] Parsing event type: {event_type}")

    if event_type == "push":
        # for push will render according
        try:
            request_id = payload.get("after")
            author = payload["head_commit"]["author"]["name"]
            from_branch = payload.get("ref", "").split("/")[-1]
            timestamp_raw = payload["head_commit"]["timestamp"]
            avatar_url = payload.get("repository", {}).get("owner", {}).get("avatar_url")
            # Convert to UTC format
            timestamp = datetime.fromisoformat(timestamp_raw)
            timestamp_utc = timestamp.astimezone(timezone.utc)
            formated_time = timestamp_utc.strftime("%d %B %Y %I:%M %p UTC")

            print(f"[INFO] Parsed push event: commit={request_id}, author={author}, branch={from_branch}, timestamp={formated_time}")
            return {
                "request_id": request_id,
                "author": author,
                "action": "Push",
                "from_branch": from_branch,
                "to_branch": None,
                "timestamp": formated_time,
                "avatar_url": avatar_url,
            }

        except Exception as e:
            print("[ERROR] Failed to parse push event:")
            traceback.print_exc()
            return None

    elif event_type == "pull_request":
        # for pull request we have the action as opened, closed, reopened with there diffrent timestamp status
        try:
            action = payload.get("action")
            if action == "opened":
                action = "PR_Open"
                status = "created_at"
            elif action == "closed":
                action = "PR_Closed"
                status = "closed_at"
            elif action == "reopened":
                action = "PR_Reopened"
                status = "created_at"
            request_id = payload.get("number")
            author = payload.get("pull_request", {}).get("user", {}).get("login")
            from_branch = payload.get("pull_request", {}).get("head", {}).get("ref")
            to_branch = payload.get("pull_request", {}).get("base", {}).get("ref")
            avatar_url = payload.get("pull_request", {}).get("user", {}).get("avatar_url")
            # We will get the status for timestam_raw from above if condations
            timestamp_raw = payload.get("pull_request", {}).get(status)
            # for pull request the github webhook send the timestamp in UTC format
            timestamp = datetime.strptime(timestamp_raw, "%Y-%m-%dT%H:%M:%SZ")
            timestamp = timestamp.replace(tzinfo=pytz.utc)
            formated_time = timestamp.strftime("%d %B %Y %I:%M %p UTC")
            

            print(f"[INFO] Parsed pull_request event: id={request_id}, author={author}, from={from_branch}, to={to_branch}, action={action}")
            return {
                "request_id": request_id,
                "author": author,
                "action": action,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": formated_time,
                "avatar_url": avatar_url,
            }

        except Exception as e:
            print("[ERROR] Failed to parse pull_request event:")
            traceback.print_exc()
            return None

    print(f"[WARN] Unsupported event type received: {event_type}")
    return None

# I will use this route to send notification to my mattermost server to have the mobile notification
@app.route("/", methods=["GET"])
def home():
    # Fetch all documents from the collection and return as JSON
    docs = list(collection.find())
    # Convert ObjectId to string for JSON serialization
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return jsonify(docs)

# Send data to mattermost API
def send_mattermost_message(author, action, from_branch, timestamp):
    mattermost_url = os.getenv("MATTERMOST_URL")
    if not mattermost_url:
        print("[ERROR] MATTERMOST_URL not set in environment.")
        return
    payload = {
        "username": "GitBot",
        "icon_url": "https://cdn.jsdelivr.net/gh/selfhst/icons/svg/octobot-light.svg",
        "text": f"/// {author} has {action} on {from_branch} at {timestamp}"
    }
    try:
        response = requests.post(mattermost_url, json=payload)
        print(f"[Mattermost] Message send to Mattermost with {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to send message to Mattermost: {e}")

# call send_mattermost_message function


# This is the route where out github will send the webhook
@app.route("/webhook", methods=["POST"])
def github_webhook():
    try:
        event_type = request.headers.get("X-GitHub-Event", "unknown")
        payload = request.json or json.loads(request.data)

        print(f"[INFO] Received event: {event_type}")
        parsed = parse_event(event_type, payload)

        if not parsed:
            print("[INFO] No valid data extracted from payload.")
            return jsonify({"status": "ignored", "reason": "unhandled or failed to parse"}), 202

        result = collection.insert_one(parsed)
        print(f"[INFO] Successfully inserted document with ID: {result.inserted_id}")
        # Send notification to Mattermost
        if notification_reciver == "mattermost":
            send_mattermost_message(parsed["author"], parsed["action"], parsed["from_branch"], parsed["timestamp"])
        elif notification_reciver == "slack":
            return None

        return jsonify({"status": "success", "inserted_id": str(result.inserted_id)}), 201

    except Exception as e:
        print("[ERROR] Exception during webhook processing:")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# This is route for out frontend UI to fetch the data from our database
@app.route("/api/commits", methods=["GET"])
def api_commits():
    docs = list(collection.find())
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        doc["author"] = doc.get("author", "octocat")
        doc["request_id"] = str(doc.get("request_id", "-"))
        doc["action"] = doc.get("action", "Commit")
        doc["timestamp"] = doc.get("timestamp", "-")
        doc["from_branch"] = doc.get("from_branch", "main")
        doc["to_branch"] = doc.get("to_branch", None)
    return jsonify(docs)

# HTML template commit history
commit_history_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Commit History</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f6f8fa; }
        .commit-list { max-width: 700px; margin: 40px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        .commit-item { border-bottom: 1px solid #e1e4e8; padding: 20px 24px; display: flex; align-items: center; position: relative; }
        .commit-item:last-child { border-bottom: none; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; margin-right: 18px; }
        .commit-details { flex: 1; }
        .commit-message { font-weight: 500; color: #24292e; margin-bottom: 4px; }
        .commit-meta { color: #586069; font-size: 0.95em; }
        .commit-id { font-family: monospace; color: #6a737d; font-size: 0.95em; }
        .recent-badge { position: absolute; right: 24px; top: 24px; background: #28a745; color: #fff; font-size: 0.85em; padding: 2px 10px; border-radius: 12px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="commit-list" id="commit-list">
        <h2 class="text-center py-3" style="border-bottom:1px solid #e1e4e8;">Commit History</h2>
        <!-- Commits will be rendered here by JS -->
    </div>
    <script>
    async function fetchCommits() {
        const res = await fetch('/api/commits');
        let commits = await res.json();
        // Sort by timestamp descending (most recent first)
        commits.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        const list = document.getElementById('commit-list');
        let html = `<h2 class="text-center py-3" style="border-bottom:1px solid #e1e4e8;">Commit History</h2>`;
        if (commits.length === 0) {
            html += `<div class="text-center py-5">No commits found.</div>`;
        } else {
            commits.forEach((commit, idx) => {
                let dateStr = commit.timestamp || '-';
                let meta = '';
                if (commit.action === "PR_Open") {
                    meta = `<div class="commit-meta">
                        <span>${commit.author}</span> opened a PR on <span>"${commit.from_branch}"</span> on <span>${dateStr}</span>
                    </div>`;
                } else if (commit.action === "PR_Closed") {
                    meta = `<div class="commit-meta">
                        <span>${commit.author}</span> closed a PR on <span>"${commit.from_branch}"</span> on <span>${dateStr}</span>
                    </div>`;
                } else if (commit.action === "PR_Reopened") {
                    meta = `<div class="commit-meta">
                        <span>${commit.author}</span> reopened a PR on <span>"${commit.from_branch}"</span> on <span>${dateStr}</span>
                    </div>`;
                } else if (commit.action === "PR_Merged") {
                    meta = `<div class="commit-meta">
                        <span>${commit.author}</span> merged a PR on <span>"${commit.from_branch}"</span> on <span>${dateStr}</span>
                    </div>`;
                } else if (commit.action === "Push") {
                    meta = `<div class="commit-meta">
                        <span>${commit.author}</span> pushed to <span>"${commit.from_branch}"</span> on <span>${dateStr}</span>
                    </div>`;
                }
                html += `
                <div class="commit-item">
                    <img class="avatar" src="${commit.avatar_url || 'octocat'}.png" onerror="this.src='https://github.com/octocat.png'" alt="avatar">
                    <div class="commit-details">
                        <div class="commit-message">${commit.action} on with #<span class="commit-id">${commit.request_id.slice(0,7)}</span></div>
                        ${meta}
                    </div>
                    ${idx === 0 ? '<span class="recent-badge">Recent</span>' : ''}
                </div>
                `;
            });
        }
        list.innerHTML = html;
    }
    fetchCommits();
    setInterval(fetchCommits, 15000);
    </script>
</body>
</html>
'''

@app.route("/commits", methods=["GET"])
def commit_history():
    docs = list(collection.find())
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        # Fallbacks for missing fields
        doc["author"] = doc.get("author", "octocat")
        doc["request_id"] = str(doc.get("request_id", "-"))
        doc["action"] = doc.get("action", "Commit")
        doc["timestamp"] = doc.get("timestamp", "-")
        doc["from_branch"] = doc.get("from_branch", "main")
        doc["to_branch"] = doc.get("to_branch", None)
    return render_template_string(commit_history_template, commits=docs)

if __name__ == "__main__":
    print("[STARTING] Flask server is starting on port 5000...")
    app.run(port=5000, debug=True)
