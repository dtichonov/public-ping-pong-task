import requests
import sys

services = [
    {"host": "127.0.0.1", "port": 9000},
    {"host": "127.0.0.1", "port": 9001},
]


def send_command(command, pong_time_ms=0):
    service1_url = f"http://{services[0]['host']}:{services[0]['port']}"
    service1_url_control = f"{service1_url}/control"
    service2_url = f"http://{services[1]['host']}:{services[1]['port']}"
    service2_url_control = f"{service2_url}/control"

    if command == "start":
        if pong_time_ms <= 0:
            print("Please provide a valid pong time in ms")
            return

        # TODO: Wrap to check if services are started
        requests.post(service1_url_control, json={"command": "start", "pong_time": pong_time_ms, "opponent": service2_url})
        requests.post(service2_url_control, json={"command": "start", "pong_time": pong_time_ms, "opponent": service1_url})

        print(f"Started with pont time = {pong_time_ms}")
    elif command in ["pause", "resume", "stop"]:

        # TODO: Wrap to check if services are started
        requests.post(service1_url_control, json={"command": command})
        requests.post(service2_url_control, json={"command": command})

        print(f"{command}ed")
    else:
        print("Invalid command")


def main():
    if len(sys.argv) < 2:
        print("Usage: <command> <param>")
        print("""
        Usage:
            * start <pong time in ms>
            * pause
            * resume
            * stop 
        """)
        sys.exit(1)

    command = sys.argv[1]

    pong_time_ms = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    send_command(command, pong_time_ms)


if __name__ == "__main__":
    main()
