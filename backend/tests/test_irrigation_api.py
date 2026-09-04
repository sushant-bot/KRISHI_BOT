from datetime import datetime, timezone


def create_zone(client):
    farm = client.post("/api/farms", json={"name": "Irrigation Farm"}).json()
    return client.post(
        f"/api/farms/{farm['id']}/zones",
        json={"code": "B2", "name": "North plot"},
    ).json()


def test_irrigation_reaches_target(client):
    zone = create_zone(client)
    command = client.post(
        "/api/irrigation/command",
        json={"zone_id": zone["id"], "action": "START", "target_water_liters": 5},
    )
    assert command.status_code == 201
    assert command.json()["status"] == "ACTIVE"

    flow = client.post(
        "/api/irrigation/flow",
        json={
            "zone_id": zone["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "flow_rate": 2.4,
            "water_delivered": 5.6,
            "pump_status": "ON",
        },
    )
    assert flow.status_code == 201
    history = client.get("/api/irrigation/history")
    assert history.json()[0]["status"] == "COMPLETED"
    assert client.get(
        f"/api/irrigation/status?zone_id={zone['id']}"
    ).json() is None


def test_zero_flow_marks_failure_and_creates_alert(client):
    zone = create_zone(client)
    started = client.post(
        "/api/irrigation/command",
        json={"zone_id": zone["id"], "action": "START"},
    )
    assert started.status_code == 201

    flow = client.post(
        "/api/irrigation/flow",
        json={
            "zone_id": zone["id"],
            "flow_rate": 0,
            "water_delivered": 0,
            "pump_status": "ON",
        },
    )
    assert flow.status_code == 201
    history = client.get(
        f"/api/irrigation/history?zone_id={zone['id']}"
    ).json()
    assert history[0]["status"] == "FAILED"
    assert history[0]["fault_message"] == "Pump is on but water flow is zero."


def test_irrigation_requires_active_event(client):
    zone = create_zone(client)
    response = client.post(
        "/api/irrigation/flow",
        json={
            "zone_id": zone["id"],
            "flow_rate": 1,
            "water_delivered": 1,
            "pump_status": "ON",
        },
    )
    assert response.status_code == 409
