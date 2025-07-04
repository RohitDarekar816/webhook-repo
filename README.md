# GitHub Webhook Listener & Commit History UI

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green?logo=mongodb)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🚀 Project Overview

This project is a **GitHub Webhook Listener** built with Flask and MongoDB. It receives webhook events (push, pull requests) from GitHub, stores them in a database, and provides a modern, GitHub-like UI to view commit and PR history. It also exposes REST API endpoints for integration and automation.

---

## ✨ Features

- Receive and parse GitHub webhook events (push, PR open/close/reopen)
- Store commit and PR data in MongoDB
- REST API to fetch commit/PR history
- Beautiful, responsive UI for commit history (Bootstrap 5)
- Avatar support via GitHub usernames
- Easy deployment and configuration
- Extensible for notifications (e.g., Mattermost)

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** MongoDB
- **Frontend:** HTML, Bootstrap 5, Vanilla JS
- **Other:** python-dotenv, pymongo, pytz

---

## ⚡ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RohitDarekar816/webhook-repo.git
   cd webhook-repo
   ```

2. **Create a virtual environment & activate:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Create a `.env` file in the `webhook-repo/` directory:
     ```env
     MONGO_URL=mongodb+srv://<username>:<password>@<cluster-url>/<dbname>?retryWrites=true&w=majority
     ```

---

## 🏃 Running the App

```bash
python app.py
```
- The server will start on [http://localhost:5000](http://localhost:5000)

---

## 🔗 API Endpoints

| Method | Endpoint         | Description                       |
|--------|------------------|-----------------------------------|
| GET    | `/`              | All webhook data (JSON)           |
| POST   | `/webhook`       | GitHub webhook receiver           |
| GET    | `/api/commits`   | All commits/PRs (JSON)            |
| GET    | `/commits`       | Commit history UI (HTML)          |

---

## 🖥️ Frontend UI

- Visit [http://localhost:5000/commits](http://localhost:5000/commits) to view a modern, GitHub-style commit/PR history.
- The UI auto-refreshes every 15 seconds.

---

## 📦 Example GitHub Webhook Payloads

<details>
<summary>Push Event</summary>

```json
{
  "after": "commitsha123...",
  "head_commit": {
    "author": { "name": "octocat" },
    "timestamp": "2024-05-01T12:34:56+00:00"
  },
  "ref": "refs/heads/main"
}
```
</details>

<details>
<summary>Pull Request Event</summary>

```json
{
  "action": "opened",
  "number": 42,
  "pull_request": {
    "user": { "login": "octocat" },
    "head": { "ref": "feature-branch" },
    "base": { "ref": "main" },
    "created_at": "2024-05-01T12:34:56Z"
  }
}
```
</details>

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!<br>
Feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact

- **Author:** Rohit
- **Email:** [rohitdarekar816@gmail.com](mailto:your-email@example.com)
- **GitHub:** [Rohitdarekar816](https://github.com/your-github-username)

---

<p align="center">
  <a href="https://www.buymeacoffee.com/rohitdarekar"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=rohitdarekar&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" /></a>
</p>

<p align="center">
  <img src="bmc_qr.png" alt="Buy Me a Coffee QR" width="200" />
  <br/>
  <em>Scan to support me on Buy Me a Coffee!</em>
</p>

---

> _Built with ❤️ for DevOps, Automation, and Open Source._
