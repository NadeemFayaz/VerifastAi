import subprocess
import time
import os
import sys

def check_docker_running():
    """Check if Docker daemon is running"""
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def is_qdrant_container_running():
    """Check if Qdrant container is already running"""
    result = subprocess.run(
        ["docker", "ps", "--filter", "ancestor=qdrant/qdrant", "--format", "{{.ID}}"],
        capture_output=True,
        text=True
    )
    return bool(result.stdout.strip())

def start_qdrant_container():
    """Start the Qdrant container"""
    print("Starting Qdrant container...")
    subprocess.run(
        ["docker", "run", "-d", "-p", "6333:6333", "-p", "6334:6334", "qdrant/qdrant"],
        check=True
    )
    # Wait for container to be fully operational
    print("Waiting for Qdrant container to initialize...")
    time.sleep(5)

def run_vector_storage():
    """Run the vector storage script"""
    script_path = os.path.join(os.path.dirname(__file__), "vector_db", "store_in_qdrant.py")
    print(f"Running vector storage script: {script_path}")
    
    subprocess.run([sys.executable, script_path], check=True)

def init_server():
    if not check_docker_running():
        print("Error: Docker is not running. Please start Docker and try again.")
        sys.exit(1)
    
    if not is_qdrant_container_running():
        start_qdrant_container()
    else:
        print("Qdrant container is already running.")
    
    run_vector_storage()
    print("Process completed successfully.")

