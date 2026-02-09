"""Tests for the FastAPI activities application"""

import pytest


def test_read_root(client):
    """Test that the root endpoint redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test that we can retrieve all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    assert "Basketball" in activities
    assert "Soccer" in activities
    assert "Art Club" in activities
    assert "Drama Club" in activities
    assert "Science Club" in activities
    assert "Debate Team" in activities


def test_activity_structure(client):
    """Test that each activity has the correct structure"""
    response = client.get("/activities")
    activities = response.json()
    
    for name, details in activities.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_for_activity_success(client):
    """Test successfully signing up for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=test@example.com"
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "message" in result
    assert "test@example.com" in result["message"]
    assert "Chess Club" in result["message"]
    
    # Verify the participant was added
    activities = client.get("/activities").json()
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_duplicate_email(client):
    """Test that signing up with duplicate email fails"""
    email = "duplicate@example.com"
    
    # First signup should succeed
    response = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )
    assert response.status_code == 400
    
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_nonexistent_activity(client):
    """Test that signing up for a non-existent activity fails"""
    response = client.post(
        "/activities/NonExistentActivity/signup?email=test@example.com"
    )
    assert response.status_code == 404
    
    result = response.json()
    assert "not found" in result["detail"]


def test_unregister_success(client):
    """Test successfully unregistering from an activity"""
    email = "unregister_test@example.com"
    
    # First, sign up for an activity
    client.post(
        f"/activities/Programming%20Class/signup?email={email}"
    )
    
    # Verify the participant was added
    activities = client.get("/activities").json()
    assert email in activities["Programming Class"]["participants"]
    
    # Now unregister
    response = client.delete(
        f"/activities/Programming%20Class/unregister?email={email}"
    )
    assert response.status_code == 200
    
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email in result["message"]
    
    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities["Programming Class"]["participants"]


def test_unregister_not_signed_up(client):
    """Test that unregistering someone who isn't signed up fails"""
    response = client.delete(
        "/activities/Basketball/unregister?email=notregistered@example.com"
    )
    assert response.status_code == 400
    
    result = response.json()
    assert "not signed up" in result["detail"]


def test_unregister_nonexistent_activity(client):
    """Test that unregistering from a non-existent activity fails"""
    response = client.delete(
        "/activities/NonExistentActivity/unregister?email=test@example.com"
    )
    assert response.status_code == 404
    
    result = response.json()
    assert "not found" in result["detail"]


def test_full_workflow(client):
    """Test a complete workflow: signup, verify, unregister, verify"""
    email = "workflow@example.com"
    activity = "Soccer"
    
    # Get initial participant count
    initial_activities = client.get("/activities").json()
    initial_count = len(initial_activities[activity]["participants"])
    
    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == initial_count + 1
    
    # Unregister
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == initial_count
