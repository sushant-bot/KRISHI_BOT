from datetime import datetime, timezone


def create_zone(client):
    farm = client.post("/api/farms", json={"name": "Decision Farm"}).json()
    zone = client.post(
        f"/api/farms/{farm['id']}/zones",
        json={"code": "C1", "name": "East plot"},
    ).json()
    return farm, zone


def test_decision_context_aggregates_persisted_inputs(client):
    farm, zone = create_zone(client)
    client.post(
        "/api/sensors/readings",
        json={
            "zone_id": zone["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "soil_moisture": 24,
            "soil_temperature": 33.2,
            "light_intensity": 42000,
        },
    )
    image = client.post(
        "/api/images",
        json={
            "farm_id": farm["id"],
            "zone_id": zone["id"],
            "image_path": "s3://agrovisor/context/image.jpg",
        },
    )
    assert image.status_code == 201
    ai_result = client.post(
        "/api/ai/analyze",
        json={"image_id": image.json()["id"], "crop_health": "Healthy", "provider": "model-v1"},
    )
    assert ai_result.status_code == 201

    context = client.get(
        f"/api/zones/{zone['id']}/decision-context"
    )
    assert context.status_code == 200
    body = context.json()
    assert body["latest_sensor"]["soil_moisture"] == 24
    assert body["latest_ai_result"]["crop_health"] == "Healthy"
    assert body["active_irrigation"] is None


def test_external_decision_result_and_health_history(client):
    _, zone = create_zone(client)
    result = client.post(
        "/api/decisions/analyze",
        json={
            "zone_id": zone["id"],
            "irrigation_priority": "CRITICAL",
            "water_stress": "HIGH",
            "heat_stress": "HIGH",
            "disease_spread_risk": "LOW",
            "yield_risk": "MEDIUM",
            "farm_health_score": 42,
            "advisory": "Review Zone C1 irrigation.",
            "provider": "decision-engine-v1",
        },
    )
    assert result.status_code == 201
    health = client.get(f"/api/zones/{zone['id']}/health")
    assert health.status_code == 200
    assert health.json()["farm_health_score"] == 42
    risks = client.get(f"/api/zones/{zone['id']}/risks")
    assert risks.status_code == 200
    assert risks.json()[0]["provider"] == "decision-engine-v1"


def test_decision_score_is_validated(client):
    _, zone = create_zone(client)
    response = client.post(
        "/api/decisions/analyze",
        json={"zone_id": zone["id"], "farm_health_score": 101, "provider": "engine"},
    )
    assert response.status_code == 422
