"""
Timer and Notification Microservice
CS361 - Sprint 2

Communication:
  REQ/REP socket on tcp://localhost:5557  — request/response for actions
  PUSH socket on tcp://localhost:5558     — outbound timer-expired notifications

Supported actions (send as JSON):
  start_timer   : {"action": "start_timer",   "duration": <seconds>, "item_name": <str, optional>}
  cancel_timer  : {"action": "cancel_timer",  "timer_id": <str>}
  get_status    : {"action": "get_status",    "timer_id": <str>}
"""

import zmq
import json
import uuid
import threading
from datetime import datetime, timezone


# ── In-memory timer store ────────────────────────────────────────────────────
# { timer_id: {"item_name": str, "duration": int, "end_time": str,
#              "cancelled": bool, "expired": bool, "_thread": Thread} }
_timers: dict = {}
_lock = threading.Lock()


# ── Notification sender ──────────────────────────────────────────────────────
def _push_notification(push_socket, timer_id: str, item_name: str):
    payload = {
        "type": "timer_expired",
        "timer_id": timer_id,
        "item_name": item_name,
        "message": "Your scheduled event is starting now!",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        push_socket.send_string(json.dumps(payload))
    except zmq.ZMQError:
        pass


# ── Timer thread ─────────────────────────────────────────────────────────────
def _run_timer(timer_id: str, duration: int, push_socket):
    """Sleep for `duration` seconds then fire the notification (unless cancelled)."""
    event = threading.Event()
    with _lock:
        _timers[timer_id]["_event"] = event

    fired = not event.wait(timeout=duration)   # wait returns True if set (cancelled)
    if fired:
        with _lock:
            if timer_id in _timers and not _timers[timer_id]["cancelled"]:
                _timers[timer_id]["expired"] = True
                item_name = _timers[timer_id]["item_name"]
        _push_notification(push_socket, timer_id, item_name)


# ── Action handlers ───────────────────────────────────────────────────────────
def handle_start_timer(data: dict, push_socket) -> dict:
    duration = data.get("duration")
    if not isinstance(duration, int) or duration <= 0:
        return {"status": "error", "action": "start_timer",
                "message": "duration must be a positive integer (seconds)"}

    item_name = data.get("item_name", "")
    timer_id = "tmr_" + uuid.uuid4().hex[:8]
    end_time = datetime.now(timezone.utc).replace(microsecond=0)
    from datetime import timedelta
    end_time = end_time + timedelta(seconds=duration)
    end_time_str = end_time.isoformat()

    timer_record = {
        "item_name": item_name,
        "duration": duration,
        "end_time": end_time_str,
        "cancelled": False,
        "expired": False,
    }

    with _lock:
        _timers[timer_id] = timer_record

    t = threading.Thread(target=_run_timer, args=(timer_id, duration, push_socket),
                         daemon=True)
    t.start()
    with _lock:
        _timers[timer_id]["_thread"] = t

    return {
        "status": "ok",
        "action": "start_timer",
        "data": {
            "timer_id": timer_id,
            "item_name": item_name,
            "duration": duration,
            "end_time": end_time_str,
        },
    }


def handle_cancel_timer(data: dict) -> dict:
    timer_id = data.get("timer_id", "").strip()
    if not timer_id:
        return {"status": "error", "action": "cancel_timer",
                "message": "timer_id is required"}

    with _lock:
        timer = _timers.get(timer_id)

    if timer is None:
        return {"status": "error", "action": "cancel_timer",
                "message": f"No timer found with id '{timer_id}'"}
    if timer["cancelled"]:
        return {"status": "error", "action": "cancel_timer",
                "message": f"Timer '{timer_id}' is already cancelled"}
    if timer["expired"]:
        return {"status": "error", "action": "cancel_timer",
                "message": f"Timer '{timer_id}' has already expired and cannot be cancelled"}

    with _lock:
        _timers[timer_id]["cancelled"] = True
        event = _timers[timer_id].get("_event")

    if event:
        event.set()   # wake the timer thread so it exits immediately

    return {
        "status": "ok",
        "action": "cancel_timer",
        "data": {
            "timer_id": timer_id,
            "message": f"Timer '{timer_id}' has been successfully cancelled.",
        },
    }


def handle_get_status(data: dict) -> dict:
    timer_id = data.get("timer_id", "").strip()
    if not timer_id:
        return {"status": "error", "action": "get_status",
                "message": "timer_id is required"}

    with _lock:
        timer = _timers.get(timer_id)

    if timer is None:
        return {"status": "error", "action": "get_status",
                "message": f"No timer found with id '{timer_id}'"}

    now = datetime.now(timezone.utc)
    end = datetime.fromisoformat(timer["end_time"])
    remaining = max(0, int((end - now).total_seconds()))

    return {
        "status": "ok",
        "action": "get_status",
        "data": {
            "timer_id": timer_id,
            "item_name": timer["item_name"],
            "duration": timer["duration"],
            "end_time": timer["end_time"],
            "remaining_seconds": remaining,
            "cancelled": timer["cancelled"],
            "expired": timer["expired"],
        },
    }


# ── Main server loop ──────────────────────────────────────────────────────────
def run():
    context = zmq.Context()

    # REQ/REP socket — synchronous request handling
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://*:5557")

    # PUSH socket — fire-and-forget notifications to the main program
    push_socket = context.socket(zmq.PUSH)
    push_socket.bind("tcp://*:5558")

    print("Timer and Notification Microservice is running.")
    print("  REQ/REP  -> tcp://localhost:5557")
    print("  PUSH     -> tcp://localhost:5558  (timer-expired notifications)")
    print("Press Ctrl-C to stop.\n")

    poller = zmq.Poller()
    poller.register(rep_socket, zmq.POLLIN)

    try:
        while True:
            # Poll with 1-second timeout so Ctrl-C is never blocked on Windows
            events = dict(poller.poll(timeout=1000))
            if rep_socket not in events:
                continue

            raw = rep_socket.recv_string()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                rep_socket.send_string(json.dumps(
                    {"status": "error", "message": "Invalid JSON"}))
                continue

            action = data.get("action", "")

            if action == "start_timer":
                reply = handle_start_timer(data, push_socket)
            elif action == "cancel_timer":
                reply = handle_cancel_timer(data)
            elif action == "get_status":
                reply = handle_get_status(data)
            else:
                reply = {"status": "error",
                         "message": f"Unknown action '{action}'. "
                                    "Valid actions: start_timer, cancel_timer, get_status"}

            rep_socket.send_string(json.dumps(reply))

    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        rep_socket.close()
        push_socket.close()
        context.term()


if __name__ == "__main__":
    run()
