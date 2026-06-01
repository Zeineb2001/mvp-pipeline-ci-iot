from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

GITHUB_OWNER = "Zeineb2001"
GITHUB_REPO = "mvp-pipeline-ci-iot"
WORKFLOW_FILE = "generate-config.yml"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    project_name = request.form["project_name"]
    device_id = request.form["device_id"]
    mqtt_host = request.form["mqtt_host"]
    mqtt_port = request.form["mqtt_port"]

    monitoring = "true" if request.form.get("monitoring") else "false"
    security = "true" if request.form.get("security") else "false"

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "ref": "main",
        "inputs": {
            "projectName": project_name,
            "deviceId": device_id,
            "mqttHost": mqtt_host,
            "mqttPort": mqtt_port,
            "monitoring": monitoring,
            "security": security
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 204:
        return """
        <h2>Pipeline CI déclenché avec succès ✅</h2>
        <p>Va dans GitHub → Actions pour télécharger l'artifact généré.</p>
        <a href="/">Retour</a>
        """
    else:
        return f"""
        <h2>Erreur lors du déclenchement du pipeline ❌</h2>
        <p>Status code: {response.status_code}</p>
        <pre>{response.text}</pre>
        <a href="/">Retour</a>
        """, 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)