from flask import Flask, render_template, request
import os
import yaml

app = Flask(__name__)

CONFIG_DIR = "configs"
os.makedirs(CONFIG_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    project_name = request.form["project_name"]
    device_id = request.form["device_id"]
    mqtt_host = request.form["mqtt_host"]
    mqtt_port = int(request.form["mqtt_port"])

    monitoring = True if request.form.get("monitoring") else False
    security = True if request.form.get("security") else False

    config = {
        "projectName": project_name,
        "deviceId": device_id,
        "protocol": "MQTT",
        "mqtt": {
            "host": mqtt_host,
            "port": mqtt_port
        },
        "monitoring": monitoring,
        "security": security
    }

    config_path = os.path.join(CONFIG_DIR, "config.yaml")

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False)

    return """
    <h2>Configuration générée avec succès ✅</h2>
    <p>Le fichier <b>configs/config.yaml</b> a été créé.</p>
    <p>Maintenant fais :</p>
    <pre>
git add configs/config.yaml
git commit -m "Generate IoT configuration"
git push origin main
    </pre>
    <p>Après le push, GitHub Actions va lancer le pipeline automatiquement.</p>
    <a href="/">Retour</a>
    """

if __name__ == "__main__":
    app.run(debug=True, port=5000)