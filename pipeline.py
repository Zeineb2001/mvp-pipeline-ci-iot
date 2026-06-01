import os
import yaml
import zipfile
import secrets

CONFIG_FILE = "configs/config.yaml"
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "output"
ARTIFACT_DIR = "artifacts"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

print("=== CI PIPELINE STARTED ===")
print("[1] Reading configuration from WebView...")
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

project_name = config["projectName"]
device_id = config["deviceId"]
protocol = config["protocol"]
mqtt_host = config["mqtt"]["host"]
mqtt_port = int(config["mqtt"]["port"])
monitoring = config.get("monitoring", False)
security = config.get("security", False)

print("[2] Validating parameters...")
if protocol != "MQTT":
    raise Exception("Only MQTT is supported in this MVP.")

if mqtt_port < 1 or mqtt_port > 65535:
    raise Exception("Invalid MQTT port.")

print("[3] Preparing variables...")
variables = {
    "PROJECT_NAME": project_name,
    "DEVICE_ID": device_id,
    "MQTT_HOST": mqtt_host,
    "MQTT_PORT": mqtt_port,
    "MONITORING_ENABLED": str(monitoring).lower(),
    "SECURITY_ENABLED": str(security).lower(),
    "DEVICE_TOKEN": secrets.token_hex(16)
}

def generate_file(template_name, output_name):
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    output_path = os.path.join(OUTPUT_DIR, output_name)

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    for key, value in variables.items():
        content = content.replace("${" + key + "}", str(value))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated: {output_path}")
    return output_path

print("[4] Generating configuration files from templates...")
generated_files = [
    generate_file("mqtt-config.template.json", "mqtt-config.json"),
    generate_file("docker-compose.template.yml", "docker-compose.yml"),
    generate_file("env.template", ".env"),
    generate_file("README.template.md", "README.md")
]

print("[5] Creating artifact ZIP...")
artifact_path = os.path.join(ARTIFACT_DIR, f"{project_name}-setup.zip")

with zipfile.ZipFile(artifact_path, "w") as zipf:
    for file_path in generated_files:
        zipf.write(file_path, arcname=os.path.basename(file_path))

print(f"[6] Artifact created: {artifact_path}")
print("=== CI PIPELINE FINISHED SUCCESSFULLY ===")