from flask import Flask, render_template, request, send_file
import os
import zipfile
import secrets

app = Flask(__name__)

TEMPLATE_DIR = "templates"
OUTPUT_DIR = "generated"
ARTIFACT_DIR = "artifacts"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def render_template_file(template_name, output_name, variables):
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    output_path = os.path.join(OUTPUT_DIR, output_name)

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    for key, value in variables.items():
        content = content.replace("${" + key + "}", str(value))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path

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

    if not mqtt_port.isdigit() or not (1 <= int(mqtt_port) <= 65535):
        return "Erreur : port MQTT invalide", 400

    device_token = secrets.token_hex(16)

    variables = {
        "PROJECT_NAME": project_name,
        "DEVICE_ID": device_id,
        "MQTT_HOST": mqtt_host,
        "MQTT_PORT": mqtt_port,
        "MONITORING_ENABLED": monitoring,
        "SECURITY_ENABLED": security,
        "DEVICE_TOKEN": device_token
    }

    generated_files = []
    generated_files.append(render_template_file("mqtt-config.template.json", "mqtt-config.json", variables))
    generated_files.append(render_template_file("docker-compose.template.yml", "docker-compose.yml", variables))
    generated_files.append(render_template_file("env.template", ".env", variables))
    generated_files.append(render_template_file("README.template.md", "README.md", variables))

    artifact_path = os.path.join(ARTIFACT_DIR, f"{project_name}-setup.zip")

    with zipfile.ZipFile(artifact_path, "w") as zipf:
        for file_path in generated_files:
            zipf.write(file_path, arcname=os.path.basename(file_path))

    return send_file(artifact_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
