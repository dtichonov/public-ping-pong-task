from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import threading
import time
import requests

app = FastAPI()

state = {"running": False, "pong_time_ms": 1000, "opponent": None}
state_lock = threading.Lock()


@app.post("/control")
async def handle_control(request: Request):
    """
    Control plane for cli

    :param request:
    :return:
    """
    # TODO: Validate request
    data = await request.json()
    command = data.get("command")
    pong_time_ms = data.get("pong_time", 1000)
    opponent = data.get("opponent")

    with state_lock:
        if command == "start":
            if state["running"]:
                return {"status": "already running"}

            state.update({"running": True, "pong_time_ms": pong_time_ms, "opponent": opponent})
            threading.Thread(target=send_ping, daemon=True).start()

            return JSONResponse({"status": "game started"}, status_code=200)
        elif command == "pause":
            state["running"] = False

            return JSONResponse({"status": "game paused"}, status_code=200)
        elif command == "resume":
            if state["running"]:
                return {"status": "already running"}

            state["running"] = True
            threading.Thread(target=send_ping, daemon=True).start()

            return JSONResponse({"status": "game resumed"}, status_code=200)
        elif command == "stop":
            state["running"] = False
            state["opponent"] = None

            return JSONResponse({"status": "game stopped"}, status_code=200)
        else:
            return JSONResponse({"status": "unknown command"}, status_code=400)


@app.get("/ping")
async def handle_ping():
    """
    Handle ping request

    :return:
    """
    with state_lock:
        if not state["running"]:
            return {"message": "game is paused"}

        pong_time_ms = state["pong_time_ms"]

    time.sleep(pong_time_ms / 1000.0)

    return JSONResponse({"message": "pong"}, status_code=200)


def send_ping():
    """
    Send a ping request

    :return:
    """
    while True:
        with state_lock:
            if not state["running"]:
                break
            opponent_url = state["opponent"]

        if opponent_url:
            try:
                response = requests.get(f"{opponent_url}/ping")

                if response.status_code == 200:
                    print(f"Received response: {response.json()}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to ping opponent: {e}")
