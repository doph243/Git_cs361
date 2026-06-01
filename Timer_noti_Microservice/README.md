# Timer and Notification Microservice

**CS361 – Sprint 2 | Hoang Phuc Do & Alex Jones**

---

## Description

This microservice lets any program start a countdown timer, cancel an active timer, or check its status. When a timer expires, the microservice **automatically pushes a JSON notification** to the main program without being asked — no polling required.

---

## Communication Protocol

| Channel | Pattern | Address | Purpose |
|---------|---------|---------|---------|
| Request / Response | ZeroMQ REQ ↔ REP | `tcp://localhost:5557` | Send actions, receive immediate replies |
| Notifications | ZeroMQ PUSH → PULL | `tcp://localhost:5558` | Receive timer-expired alerts |

Both channels send/receive **JSON-encoded strings**.

---

## How to REQUEST Data

Connect a `zmq.REQ` socket to `tcp://localhost:5557` and send a JSON string. The `"action"` field selects what the microservice does.

### Action: `start_timer`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | yes | `"start_timer"` |
| `duration` | int | yes | Countdown length in **seconds** |
| `item_name` | string | no | Label for the timer (e.g., grocery item) |

```python
import zmq, json

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5557")

request = {
    "action": "start_timer",
    "duration": 86400,   # 24 hours in seconds
    "item_name": "Milk"
}
socket.send_string(json.dumps(request))
reply = json.loads(socket.recv_string())
print(reply)
```

### Action: `cancel_timer`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | yes | `"cancel_timer"` |
| `timer_id` | string | yes | ID returned by `start_timer` |

```python
request = {
    "action": "cancel_timer",
    "timer_id": "tmr_a1b2c3d4"
}
socket.send_string(json.dumps(request))
reply = json.loads(socket.recv_string())
print(reply)
```

### Action: `get_status`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | yes | `"get_status"` |
| `timer_id` | string | yes | ID returned by `start_timer` |

```python
request = {
    "action": "get_status",
    "timer_id": "tmr_a1b2c3d4"
}
socket.send_string(json.dumps(request))
reply = json.loads(socket.recv_string())
print(reply)
```

---

## How to RECEIVE Data

### Synchronous Replies (port 5557)

Every action on the REQ/REP socket receives an immediate JSON reply. The reply always has a `"status"` field (`"ok"` or `"error"`) and an `"action"` field mirroring what was requested.

**`start_timer` reply:**
```json
{
    "status": "ok",
    "action": "start_timer",
    "data": {
        "timer_id": "tmr_002",
        "item_name": "Milk",
        "duration": 86400,
        "end_time": "2026-05-15T10:00:00+00:00"
    }
}
```

**`cancel_timer` reply:**
```json
{
    "status": "ok",
    "action": "cancel_timer",
    "data": {
        "timer_id": "tmr_002",
        "message": "Timer 'tmr_002' has been successfully cancelled."
    }
}
```

**`get_status` reply:**
```json
{
    "status": "ok",
    "action": "get_status",
    "data": {
        "timer_id": "tmr_002",
        "item_name": "Milk",
        "duration": 86400,
        "end_time": "2026-05-15T10:00:00+00:00",
        "remaining_seconds": 84312,
        "cancelled": false,
        "expired": false
    }
}
```

**Error reply (any action):**
```json
{
    "status": "error",
    "action": "cancel_timer",
    "message": "No timer found with id 'tmr_badid'"
}
```

### Timer-Expired Notifications (port 5558)

Connect a `zmq.PULL` socket to `tcp://localhost:5558`. When any timer expires the microservice sends a notification **automatically** — you do not need to poll.

```python
import zmq, json

context = zmq.Context()
pull = context.socket(zmq.PULL)
pull.connect("tcp://localhost:5558")

# Blocks until a notification arrives
notification = json.loads(pull.recv_string())
print(notification)
```

**Notification payload:**
```json
{
    "type": "timer_expired",
    "timer_id": "tmr_002",
    "item_name": "Milk",
    "message": "Your scheduled event is starting now!",
    "timestamp": "2026-05-15T10:00:00+00:00"
}
```

---

## UML Sequence Diagram

```
Main Program                        Microservice (port 5557)         Notification Thread (port 5558)
     |                                        |                                  |
     |  REQ: {"action":"start_timer",         |                                  |
     |         "duration":5,                  |                                  |
     |         "item_name":"Milk"}            |                                  |
     |--------------------------------------->|                                  |
     |                                        |--- spawn timer thread (5 s) ---->|
     |  REP: {"status":"ok",                  |                                  |
     |         "data":{"timer_id":"tmr_002",  |                                  |
     |                  "end_time":"..."}}    |                                  |
     |<---------------------------------------|                                  |
     |                                        |                   [5 seconds pass]
     |  REQ: {"action":"get_status",          |                                  |
     |         "timer_id":"tmr_002"}          |                                  |
     |--------------------------------------->|                                  |
     |  REP: {"status":"ok",                  |                                  |
     |         "data":{"remaining_seconds":3, |                                  |
     |                  "expired":false}}     |                                  |
     |<---------------------------------------|                                  |
     |                                        |                  [timer fires]   |
     |                                        |<-- PUSH notification ------------|
     |  PULL: {"type":"timer_expired",        |                                  |
     |          "timer_id":"tmr_002",         |                                  |
     |          "message":"Your scheduled..."}|                                  |
     |<=======================================|                                  |
     |                                        |                                  |
     |  REQ: {"action":"cancel_timer",        |                                  |
     |         "timer_id":"tmr_002"}          |                                  |
     |--------------------------------------->|                                  |
     |  REP: {"status":"error",               |                                  |
     |         "message":"Timer has already   |                                  |
     |          expired..."}                  |                                  |
     |<---------------------------------------|                                  |
```

---

## How the Programs Communicate (No Direct Calls)

The test program and microservice are **never imported into each other** and never call each other's functions directly. They are two separate processes that communicate exclusively through ZeroMQ sockets over TCP.

**Test program side** (`test_microservice.py`):

```python
# Lines 58-62 — connects a REQ socket; sends JSON, receives JSON back
req = context.socket(zmq.REQ)
req.connect("tcp://localhost:5557")       # no import of microservice.py

# Lines 64-68 — connects a PULL socket to receive timer-expired notifications
pull = context.socket(zmq.PULL)
pull.connect("tcp://localhost:5558")      # microservice pushes here when a timer fires
```

**Microservice side** (`microservice.py`):

```python
# Lines 175-181 — binds both sockets and waits; has no knowledge of who connects
rep_socket = context.socket(zmq.REP)
rep_socket.bind("tcp://*:5557")           # no import of test_microservice.py

push_socket = context.socket(zmq.PUSH)
push_socket.bind("tcp://*:5558")
```

Neither file contains `import microservice` or `import test_microservice`. All data exchanged is plain JSON over the two ZeroMQ channels described in the Communication Protocol table above.

---

## Running the Microservice

**Requirements:**
```
pip install pyzmq
```

**Start the server** (from inside the `timer_notification_microservice` folder):
```
python microservice.py
```

**Run the test program** (in a separate terminal, same folder):
```
python test_microservice.py
```


