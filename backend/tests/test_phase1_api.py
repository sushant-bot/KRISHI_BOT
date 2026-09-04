from datetime import datetime, timezone


def test_health_is_public(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_farm_zone_and_sensor_workflow(client):
    farm = client.post(
        "/api/farms", json={"name": "Demo Farm", "location": "Pune"}
    )
    assert farm.status_code == 201

    zone = client.post(
        f"/api/farms/{farm.json()['id']}/zones",
        json={"code": "B2", "name": "North plot"},
    )
    assert zone.status_code == 201

    reading = client.post(
        "/api/sensors/readings",
        json={
            "zone_id": zone.json()["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "soil_moisture": 24,
            "soil_temperature": 33.2,
            "light_intensity": 42000,
        },
    )
    assert reading.status_code == 201
    history = client.get(f"/api/zones/{zone.json()['id']}/readings")
    assert history.status_code == 200
    assert history.json()[0]["soil_moisture"] == 24


def test_missing_resources_and_duplicate_zone(client):
    assert client.get("/api/farms/999").status_code == 404
    farm = client.post("/api/farms", json={"name": "Farm"}).json()
    payload = {"code": "A1", "name": "First"}
    assert (
        client.post(f"/api/farms/{farm['id']}/zones", json=payload).status_code
        == 201
    )
    assert (
        client.post(f"/api/farms/{farm['id']}/zones", json=payload).status_code
        == 409
    )


def test_sensor_validation(client):
    response = client.post(
        "/api/zones/readings",
        json={"zone_id": 1, "timestamp": "bad", "soil_moisture": -1},
    )
    assert response.status_code == 422
