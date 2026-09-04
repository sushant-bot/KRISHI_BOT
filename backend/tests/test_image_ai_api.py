def create_farm_and_zone(client):
    farm = client.post("/api/farms", json={"name": "Image Farm"}).json()
    zone = client.post(
        f"/api/farms/{farm['id']}/zones",
        json={"code": "A1", "name": "South plot"},
    ).json()
    return farm, zone


def test_image_metadata_and_external_ai_result(client):
    farm, zone = create_farm_and_zone(client)
    image = client.post(
        "/api/images",
        json={
            "farm_id": farm["id"],
            "zone_id": zone["id"],
            "image_path": "s3://agrovisor/farms/1/zones/1/image-001.jpg",
        },
    )
    assert image.status_code == 201
    assert client.get(f"/api/images/{image.json()['id']}").status_code == 200
    assert client.get(
        f"/api/zones/{zone['id']}/images"
    ).json()[0]["image_path"].startswith("s3://")

    result = client.post(
        "/api/ai/analyze",
        json={
            "image_id": image.json()["id"],
            "crop_health": "At Risk",
            "disease": "Possible Early Blight",
            "confidence": 0.91,
            "growth_stage": "Vegetative",
            "provider": "external-ai-service-v1",
        },
    )
    assert result.status_code == 201
    assert result.json()["provider"] == "external-ai-service-v1"
    history = client.get(f"/api/zones/{zone['id']}/ai-results")
    assert history.status_code == 200
    assert history.json()[0]["confidence"] == 0.91


def test_image_requires_matching_farm_and_zone(client):
    farm, zone = create_farm_and_zone(client)
    other_farm = client.post("/api/farms", json={"name": "Other Farm"}).json()
    response = client.post(
        "/api/images",
        json={
            "farm_id": other_farm["id"],
            "zone_id": zone["id"],
            "image_path": "/tmp/image.jpg",
        },
    )
    assert response.status_code == 409


def test_ai_result_requires_existing_image(client):
    response = client.post(
        "/api/ai/analyze",
        json={"image_id": 999, "provider": "external-ai-service-v1"},
    )
    assert response.status_code == 404


def test_ai_result_confidence_is_validated(client):
    response = client.post(
        "/api/ai/analyze",
        json={"image_id": 1, "confidence": 1.2, "provider": "external-ai-service-v1"},
    )
    assert response.status_code == 422
