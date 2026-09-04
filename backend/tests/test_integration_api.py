from datetime import datetime, timezone


def create_farm_zone(client):
    farm = client.post("/api/farms", json={"name": "Integration Farm"}).json()
    zone = client.post(
        f"/api/farms/{farm['id']}/zones",
        json={"code": "D1", "name": "West plot"},
    ).json()
    return farm, zone


def test_digital_twin_aggregates_full_zone_state(client):
    farm, zone = create_farm_zone(client)
    client.post(
        "/api/sensors/readings",
        json={
            "zone_id": zone["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "soil_moisture": 28,
            "soil_temperature": 31,
            "light_intensity": 38000,
        },
    )
    image = client.post(
        "/api/images",
        json={
            "farm_id": farm["id"],
            "zone_id": zone["id"],
            "image_path": "s3://agrovisor/integration/zone-d1.jpg",
        },
    ).json()
    client.post(
        "/api/ai/analyze",
        json={"image_id": image["id"], "crop_health": "Healthy", "provider": "model-v1"},
    )
    client.post(
        "/api/decisions/analyze",
        json={
            "zone_id": zone["id"],
            "water_stress": "LOW",
            "farm_health_score": 88,
            "provider": "decision-engine-v1",
        },
    )
    command = client.post(
        "/api/irrigation/command",
        json={"zone_id": zone["id"], "action": "START", "target_water_liters": 5},
    )
    assert command.status_code == 201

    twin = client.get(f"/api/digital-twin/zones/{zone['id']}")
    assert twin.status_code == 200
    body = twin.json()
    assert body["current"]["soil_moisture"] == 28
    assert body["latest_image"]["id"] == image["id"]
    assert body["ai"]["crop_health"] == "Healthy"
    assert body["health_score"]["farm_health_score"] == 88
    assert body["irrigation"]["status"] == "ACTIVE"
    assert body["alerts"] == []

    farm_twins = client.get("/api/digital-twin")
    assert farm_twins.status_code == 200
    assert farm_twins.json()[0]["farm_id"] == farm["id"]


def test_alerts_can_be_filtered_and_marked_read(client):
    farm, zone = create_farm_zone(client)
    started = client.post(
        "/api/irrigation/command",
        json={"zone_id": zone["id"], "action": "START"},
    )
    assert started.status_code == 201
    client.post(
        "/api/irrigation/flow",
        json={"zone_id": zone["id"], "flow_rate": 0, "water_delivered": 0, "pump_status": "ON"},
    )

    alerts = client.get(
        f"/api/alerts?farm_id={farm['id']}&unread_only=true"
    )
    assert alerts.status_code == 200
    assert len(alerts.json()) == 1
    alert_id = alerts.json()[0]["id"]
    marked = client.patch(f"/api/alerts/{alert_id}/read")
    assert marked.status_code == 200
    assert marked.json()["is_read"] is True
    assert client.get(
        f"/api/alerts?zone_id={zone['id']}&unread_only=true"
    ).json() == []


def test_digital_twin_missing_zone_returns_not_found(client):
    assert client.get("/api/digital-twin/zones/999").status_code == 404
