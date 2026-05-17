"""Tests for activities endpoints using AAA (Arrange-Act-Assert) pattern."""


def test_root_redirect(client):
    # Arrange: nothing to set up

    # Act
    resp = client.get("/", follow_redirects=False)

    # Assert
    assert resp.status_code == 307
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities(client):
    # Arrange

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity


def test_signup_and_unregister_flow(client):
    # Arrange
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure clean state: remove if already present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.post(f"/activities/{activity}/unregister", params={"email": email})

    # Act: signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert signup succeeded and participant was added
    assert resp.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

    # Act: duplicate signup
    dup = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert duplicate detected
    assert dup.status_code == 400

    # Act: unregister
    resp2 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Assert unregister succeeded
    assert resp2.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]

    # Act: unregister again -> should be 400
    resp3 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp3.status_code == 400


def test_invalid_activity(client):
    # Arrange
    bad = "Nonexistent Club"
    email = "noone@example.com"

    # Act & Assert: signup on invalid activity
    resp = client.post(f"/activities/{bad}/signup", params={"email": email})
    assert resp.status_code == 404

    # Act & Assert: unregister on invalid activity
    resp2 = client.post(f"/activities/{bad}/unregister", params={"email": email})
    assert resp2.status_code == 404
