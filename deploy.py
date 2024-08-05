import subprocess
import time
import requests
from dotenv import load_dotenv
import os
import docker

# Load environment variables from .env file
load_dotenv()

# Define variables
DOCKER_USER = "rishavsinghus"
DOCKER_PASS = os.getenv("DOCKER_PASS")
DOCKER_REPO = "rishavsinghus/sap-challenge"
SAP_NODE_APP_IMAGE = f"{DOCKER_REPO}:sap-node-app-1"
REVERSE_MESSAGE_APP_IMAGE = f"{DOCKER_REPO}:reverse-message-app"
NAMESPACE = "default"
SAP_NODE_APP_SERVICE = "sap-node-app-1"
REVERSE_MESSAGE_APP_SERVICE = "reverse-message-app"

# Define paths to applications
SAP_NODE_APP_PATH = r"C:\Users\risha\OneDrive\Desktop\coding-challenge-rishav\solution\sap-node-app-1"
REVERSE_MESSAGE_APP_PATH = r"C:\Users\risha\OneDrive\Desktop\coding-challenge-rishav\solution\reverse-message-app"

# Define paths to Kubernetes manifests
SAP_NODE_APP_MANIFEST = r"C:\Users\risha\OneDrive\Desktop\coding-challenge-rishav\solution\infra\sap-node-app-1.yaml"
REVERSE_MESSAGE_APP_MANIFEST = r"C:\Users\risha\OneDrive\Desktop\coding-challenge-rishav\solution\infra\reverse-message-app.yaml"

# Function to run shell commands
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, command)
    return result.stdout.strip()

# Function to build and push Docker images
def build_and_push_images():
    print("Building Docker images...")
    run_command(f"docker build -t {SAP_NODE_APP_IMAGE} {SAP_NODE_APP_PATH}")
    run_command(f"docker build -t {REVERSE_MESSAGE_APP_IMAGE} {REVERSE_MESSAGE_APP_PATH}")

    print("Logging into Docker Hub...")
    client = docker.from_env()
    try:
        client.login(username=DOCKER_USER, password=DOCKER_PASS)
        print("Docker login successful.")
    except docker.errors.APIError as e:
        print(f"Docker login failed: {e.explanation}")
        exit(1)

    print("Pushing Docker images...")
    try:
        run_command(f"docker push {SAP_NODE_APP_IMAGE}")
        run_command(f"docker push {REVERSE_MESSAGE_APP_IMAGE}")
    except subprocess.CalledProcessError:
        print(f"Failed to push Docker images. Please ensure you have access to the repository {DOCKER_REPO}.")
        exit(1)

# Function to deploy applications to Kubernetes
def deploy_applications():
    print("Applying Kubernetes manifests...")
    run_command(f"kubectl apply -f {SAP_NODE_APP_MANIFEST}")
    run_command(f"kubectl apply -f {REVERSE_MESSAGE_APP_MANIFEST}")

# Function to check the status of pods and services
def check_kubernetes_status():
    print("Checking Kubernetes status...")
    pods = run_command("kubectl get pods")
    print(pods)
    services = run_command("kubectl get services")
    print(services)

# Function to forward ports and print HTTP responses of applications
def forward_ports_and_print_responses():
    print("Waiting for services to be ready...")
    time.sleep(30)  # Wait for a while to ensure services are up

    try:
        print(f"Forwarding port for {SAP_NODE_APP_SERVICE} service...")
        sap_node_app_proc = subprocess.Popen(["kubectl", "port-forward", f"service/{SAP_NODE_APP_SERVICE}", "3000:3000"])
        time.sleep(5)  # Give port-forwarding some time to set up
        sap_node_app_url = "http://localhost:3000"
        print(f"Fetching response from {SAP_NODE_APP_SERVICE} at {sap_node_app_url}...")
        sap_node_app_response = requests.get(sap_node_app_url)
        print(f"Response from {SAP_NODE_APP_SERVICE}: {sap_node_app_response.text}")
    except Exception as e:
        print(f"Error fetching response from {SAP_NODE_APP_SERVICE}: {e}")
    finally:
        sap_node_app_proc.terminate()

    try:
        print(f"Forwarding port for {REVERSE_MESSAGE_APP_SERVICE} service...")
        reverse_message_app_proc = subprocess.Popen(["kubectl", "port-forward", f"service/{REVERSE_MESSAGE_APP_SERVICE}", "3001:3001"])
        time.sleep(5)  # Give port-forwarding some time to set up
        reverse_message_app_url = "http://localhost:3001"
        print(f"Fetching response from {REVERSE_MESSAGE_APP_SERVICE} at {reverse_message_app_url}...")
        reverse_message_app_response = requests.get(reverse_message_app_url)
        print(f"Response from {REVERSE_MESSAGE_APP_SERVICE}: {reverse_message_app_response.text}")
    except Exception as e:
        print(f"Error fetching response from {REVERSE_MESSAGE_APP_SERVICE}: {e}")
    finally:
        reverse_message_app_proc.terminate()

# Main script execution
def main():
    build_and_push_images()
    deploy_applications()
    check_kubernetes_status()
    forward_ports_and_print_responses()

if __name__ == "__main__":
    main()
