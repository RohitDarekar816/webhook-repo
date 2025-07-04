from operator import methodcaller
from re import X
from pymongo import MongoClient, server_api
from types import MethodType
from datetime import datetime
import json
from unittest import result
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

uri = os.getenv("MONGO_URL")

client = MongoClient(uri)
db = client["github-webhook"]
collection = db["webhook"]


app = Flask(__name__)


def parse_event(event_type, payload):
    print(f"[INFO] Parsing event type: {event_type}")

    # if event_type == "push":
    #     try:
    #         request_id = payload.get("after")
    #         author = payload["head_commit"]["author"]["name"]
    #         from_branch = payload.get("ref", "").split("/")[-1]
    #         timestamp_raw = payload["head_commit"]["timestamp"]
    #         # Convert to UTC ISO 8601 format
    #         timestamp = (
    #             datetime.fromisoformat(timestamp_raw.replace("Z", "+00:00"))
    #             .astimezone()
    #             .strftime("%Y-%m-%dT%H:%M:%SZ")
    #         )

    #         print(f"[INFO] Parsed push event: commit={request_id}, author={author}, branch={from_branch}")
    #         return {
    #             "request_id": request_id,
    #             "author": author,
    #             "action": "Push",
    #             "from_branch": from_branch,
    #             "to_branch": None,
    #             "timestamp": timestamp,
    #         }

    #     except Exception as e:
    #         print("[ERROR] Failed to parse push event:")
    #         traceback.print_exc()
    #         return None

    # elif event_type == "pull_request":
    #     try:
    #         request_id = payload.get("pull_request", {}).get("id")
    #         author = payload.get("pull_request", {}).get("user", {}).get("login")
    #         from_branch = payload.get("pull_request", {}).get("head", {}).get("ref")
    #         to_branch = payload.get("pull_request", {}).get("base", {}).get("ref")
    #         timestamp_raw = payload.get("pull_request", {}).get("created_at")
    #         # Convert to UTC ISO 8601 format if timestamp exists
    #         if timestamp_raw:
    #             timestamp = (
    #                 datetime.fromisoformat(timestamp_raw.replace("Z", "+00:00"))
    #                 .astimezone()
    #                 .strftime("%Y-%m-%dT%H:%M:%SZ")
    #             )
    #         else:
    #             timestamp = None

    #         print(f"[INFO] Parsed pull_request event: id={request_id}, author={author}, from={from_branch}, to={to_branch}")
    #         return {
    #             "request_id": request_id,
    #             "author": author,
    #             "action": "Pull_Request",
    #             "from_branch": from_branch,
    #             "to_branch": to_branch,
    #             "timestamp": timestamp,
    #         }

    #     except Exception as e:
    #         print("[ERROR] Failed to parse pull_request event:")
    #         traceback.print_exc()
    #         return None

    # elif event_type == "pull_request_review":

    # print(f"[WARN] Unsupported event type received: {event_type}")
    # return None

@app.route("/", methods=["GET"])
def home():
    # Fetch all documents from the collection and return as JSON
    docs = list(collection.find())
    # Convert ObjectId to string for JSON serialization
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return jsonify(docs)

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
        return jsonify({"status": "success", "inserted_id": str(result.inserted_id)}), 201

    except Exception as e:
        print("[ERROR] Exception during webhook processing:")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

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

# HTML template for GitHub-like commit history
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
                // Format timestamp to IST and in the required format
                let dateStr = '-';
                if (commit.timestamp && commit.timestamp !== '-') {
                    try {
                        const date = new Date(commit.timestamp);
                        // Convert to IST (UTC+5:30)
                        const utc = date.getTime() + (date.getTimezoneOffset() * 60000);
                        const istOffset = 5.5 * 60 * 60000;
                        const istDate = new Date(utc + istOffset);
                        // Format: 1st April 2021 - 9:30 PM IST
                        const day = istDate.getDate();
                        const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                        const month = monthNames[istDate.getMonth()];
                        const year = istDate.getFullYear();
                        let hours = istDate.getHours();
                        const minutes = istDate.getMinutes().toString().padStart(2, '0');
                        const ampm = hours >= 12 ? 'PM' : 'AM';
                        hours = hours % 12;
                        hours = hours ? hours : 12; // the hour '0' should be '12'
                        // Day suffix
                        const j = day % 10, k = day % 100;
                        let daySuffix = 'th';
                        if (j == 1 && k != 11) daySuffix = 'st';
                        else if (j == 2 && k != 12) daySuffix = 'nd';
                        else if (j == 3 && k != 13) daySuffix = 'rd';
                        dateStr = `${day}${daySuffix} ${month} ${year} - ${hours}:${minutes} ${ampm} IST`;
                    } catch (e) {
                        dateStr = commit.timestamp;
                    }
                }
                html += `
                <div class="commit-item">
                    <img class="avatar" src="https://github.com/${commit.author || 'octocat'}.png" onerror="this.src='https://github.com/octocat.png'" alt="avatar">
                    <div class="commit-details">
                        <div class="commit-message">${commit.action} on <span class="commit-id">${commit.request_id.slice(0,7)}</span></div>
                        <div class="commit-meta">
                            <span>${commit.author}</span> pushed to <span>"${commit.from_branch}"</span> on <span>${dateStr}</span>
                        </div>
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
