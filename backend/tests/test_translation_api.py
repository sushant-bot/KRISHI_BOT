def test_get_supported_languages(client):
    response = client.get("/api/translate/languages")
    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    languages = data["languages"]
    assert len(languages) >= 9
    codes = [lang["code"] for lang in languages]
    for required in ["en", "hi", "mr", "bn", "te", "ta", "kn", "gu", "pa"]:
        assert required in codes


def test_translate_known_soil_moisture_explanation(client):
    response = client.post(
        "/api/translate",
        json={
            "text": "Soil moisture is low. Irrigation is recommended.",
            "source_lang": "en",
            "target_lang": "hi",
        },
    )
    assert response.status_code == 200
    res = response.json()
    assert "मिट्टी" in res["translated_text"]
    assert res["target_lang"] == "hi"

    # Second call should be cached
    cached_response = client.post(
        "/api/translate",
        json={
            "text": "Soil moisture is low. Irrigation is recommended.",
            "source_lang": "en",
            "target_lang": "hi",
        },
    )
    assert cached_response.status_code == 200
    assert cached_response.json()["cached"] is True


def test_translate_flow_failure_explanation(client):
    response = client.post(
        "/api/translate",
        json={
            "text": "Pump on but flow is zero. Check water supply, pipes, and pump.",
            "source_lang": "en",
            "target_lang": "hi",
        },
    )
    assert response.status_code == 200
    assert "पंप" in response.json()["translated_text"]


def test_translate_identity_and_fallback(client):
    # Same language returns identity
    identity_res = client.post(
        "/api/translate",
        json={"text": "Hello Farmer", "source_lang": "en", "target_lang": "en"},
    )
    assert identity_res.status_code == 200
    assert identity_res.json()["translated_text"] == "Hello Farmer"

    # Unknown text fallback gracefully without error
    fallback_res = client.post(
        "/api/translate",
        json={"text": "Unseen specialized term 123", "source_lang": "en", "target_lang": "mr"},
    )
    assert fallback_res.status_code == 200
    assert fallback_res.json()["translated_text"] == "Unseen specialized term 123"
