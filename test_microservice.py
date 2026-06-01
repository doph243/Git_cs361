"""
Test program for Timer and Notification Microservice
CS361 - Sprint 2

Demonstrates:
  1. start_timer   — starts a 5-second timer with an item name
  2. get_status    — polls the timer while it counts down
  3. start_timer   — starts a second timer (for cancellation demo)
  4. cancel_timer  — cancels the second timer
  5. Notification  — waits on port 5558 and prints the notification when the
                     first timer expires

Run the microservice first:
    python microservice.py

Then in a separate terminal:
    python test_microservice.py
"""

import zmq
import json
import threading
import time


REQ_ADDR  = "tcp://localhost:5557"
PULL_ADDR = "tcp://localhost:5558"


def send_request(socket, payload: dict) -> dict:
    socket.send_string(json.dumps(payload))
    raw = socket.recv_string()
    return json.loads(raw)


def listen_for_notifications(pull_socket, stop_event: threading.Event):
    """Runs in a background thread; prints any notification that arrives."""
    pull_socket.setsockopt(zmq.RCVTIMEO, 500)   # check stop_event every 500 ms
    while not stop_event.is_set():
        try:
            raw = pull_socket.recv_string()
            notif = json.loads(raw)
            print("\n*** NOTIFICATION RECEIVED ***")
            print(f"    type      : {notif.get('type')}")
            print(f"    timer_id  : {notif.get('timer_id')}")
            print(f"    item_name : {notif.get('item_name')}")
            print(f"    message   : {notif.get('message')}")
            print(f"    timestamp : {notif.get('timestamp')}")
            print("*****************************\n")
        except zmq.Again:
            continue  # timeout — just loop


def main():
    context = zmq.Context()

    # REQ socket for sending actions
    req = context.socket(zmq.REQ)
    req.connect(REQ_ADDR)

    # PULL socket for receiving timer-expired notifications
    pull = context.socket(zmq.PULL)
    pull.connect(PULL_ADDR)

    stop_event = threading.Event()
    notif_thread = threading.Thread(target=listen_for_notifications,
                                    args=(pull, stop_event), daemon=True)
    notif_thread.start()

    print("=" * 60)
    print("Timer & Notification Microservice — Test Program")
    print("=" * 60)

    # ── Test 1: start_timer (5-second countdown for "Milk") ──────────────────
    print("\n[1] start_timer — 5 seconds, item_name='Milk'")
    reply = send_request(req, {
        "action": "start_timer",
        "duration": 5,
        "item_name": "Milk",
    })
    print("    Response:", json.dumps(reply, indent=6))
    timer_id_1 = reply.get("data", {}).get("timer_id")

    # ── Test 2: get_status on timer 1 ────────────────────────────────────────
    print("\n[2] get_status — checking timer:", timer_id_1)
    reply = send_request(req, {"action": "get_status", "timer_id": timer_id_1})
    print("    Response:", json.dumps(reply, indent=6))

    # ── Test 3: start_timer (60 seconds, will be cancelled) ──────────────────
    print("\n[3] start_timer — 60 seconds, item_name='Eggs' (will be cancelled)")
    reply = send_request(req, {
        "action": "start_timer",
        "duration": 60,
        "item_name": "Eggs",
    })
    print("    Response:", json.dumps(reply, indent=6))
    timer_id_2 = reply.get("data", {}).get("timer_id")

    # ── Test 4: cancel_timer ──────────────────────────────────────────────────
    print("\n[4] cancel_timer —", timer_id_2)
    reply = send_request(req, {"action": "cancel_timer", "timer_id": timer_id_2})
    print("    Response:", json.dumps(reply, indent=6))

    # ── Test 5: cancel already-cancelled timer (error case) ──────────────────
    print("\n[5] cancel_timer again (should return error) —", timer_id_2)
    reply = send_request(req, {"action": "cancel_timer", "timer_id": timer_id_2})
    print("    Response:", json.dumps(reply, indent=6))

    # ── Test 6: unknown action (error case) ───────────────────────────────────
    print("\n[6] unknown action 'ping' (should return error)")
    reply = send_request(req, {"action": "ping"})
    print("    Response:", json.dumps(reply, indent=6))

    # ── Test 7: get_status on non-existent timer ──────────────────────────────
    print("\n[7] get_status for bad timer_id (should return error)")
    reply = send_request(req, {"action": "get_status", "timer_id": "tmr_badid"})
    print("    Response:", json.dumps(reply, indent=6))

    # ── Wait for the 5-second timer (timer 1) to fire ────────────────────────
    print("\n[8] Waiting up to 10 s for timer 1 to expire and push a notification…")
    time.sleep(7)

    # ── get_status after expiry ───────────────────────────────────────────────
    print("\n[9] get_status after expiry —", timer_id_1)
    reply = send_request(req, {"action": "get_status", "timer_id": timer_id_1})
    print("    Response:", json.dumps(reply, indent=6))

    # ── Cleanup ───────────────────────────────────────────────────────────────
    stop_event.set()
    notif_thread.join(timeout=2)
    req.close()
    pull.close()
    context.term()

    print("\nAll tests complete.")


if __name__ == "__main__":
    main()
