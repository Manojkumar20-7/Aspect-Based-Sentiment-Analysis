import os
import sys
import subprocess
import signal
import platform

# Paths to backend and frontend directories
BACKEND_DIR = "./backend"
FRONTEND_DIR = "./frontend"

# File to store process IDs
BACKEND_PID_FILE = "backend.pid"
FRONTEND_PID_FILE = "frontend.pid"


def start():
    print("Starting backend...")
    os.chdir(BACKEND_DIR)
    backend_process = subprocess.Popen(
        ["python3", "app.py"], stdout=open("../backend.log", "w"), stderr=subprocess.STDOUT
    )
    os.chdir("..")
    with open(BACKEND_PID_FILE, "w") as f:
        f.write(str(backend_process.pid))
    
    print("Starting frontend...")
    os.chdir(FRONTEND_DIR)
    frontend_process = subprocess.Popen(
        ["npm", "start"], stdout=open("../frontend.log", "w"), stderr=subprocess.STDOUT
    )
    os.chdir("..")
    with open(FRONTEND_PID_FILE, "w") as f:
        f.write(str(frontend_process.pid))
    
    print("Backend and frontend started successfully.")


def stop():
    def terminate_process(pid_file):
        if os.path.exists(pid_file):
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            try:
                if platform.system() == "Windows":
                    subprocess.call(["taskkill", "/F", "/PID", str(pid)])
                else:
                    os.kill(pid, signal.SIGTERM)
                print(f"Stopped process with PID: {pid}")
            except Exception as e:
                print(f"Failed to stop process {pid}: {e}")
            os.remove(pid_file)

    print("Stopping backend...")
    terminate_process(BACKEND_PID_FILE)

    print("Stopping frontend...")
    terminate_process(FRONTEND_PID_FILE)

    print("Backend and frontend stopped successfully.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["start", "stop"]:
        print("Usage: python start_stop.py start|stop")
        sys.exit(1)

    command = sys.argv[1]
    if command == "start":
        start()
    elif command == "stop":
        stop()
