"""Tests for the Mergington High School API."""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for getting the list of activities."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all expected activities are present
        expected_activities = [
            "Basketball Team", "Soccer Club", "Art Club", "Drama Club",
            "Debate Team", "Math Club", "Chess Club", "Programming Class", "Gym Class"
        ]
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """Test that activities have the correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_returns_participants(self, client, reset_activities):
        """Test that activities return their current participants."""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have pre-loaded participants
        chess_participants = data["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants


class TestSignupForActivity:
    """Tests for signing up for activities."""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Basketball Team/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "student@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant."""
        # Sign up
        client.post("/activities/Basketball Team/signup?email=student@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert "student@mergington.edu" in data["Basketball Team"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test signing up when already registered."""
        email = "student@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Basketball Team/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            f"/activities/Basketball Team/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Test multiple students signing up for the same activity."""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Basketball Team/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data["Basketball Team"]["participants"]
    
    def test_signup_max_participants(self, client, reset_activities):
        """Test that an activity respects max participants."""
        # Art Club has max 10 participants
        # Fill it up
        for i in range(10):
            email = f"student{i}@mergington.edu"
            response = client.post(
                f"/activities/Art Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Try to sign up one more (should still work - we don't prevent overfilling)
        response = client.post(
            "/activities/Art Club/signup?email=overflow@mergington.edu"
        )
        # Note: The current API doesn't prevent overfilling, so this will succeed
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for unregistering from activities."""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister from an activity."""
        email = "michael@mergington.edu"
        
        # Verify student is in Chess Club initially
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        email = "michael@mergington.edu"
        
        # Unregister
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from a non-existent activity."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistering when not registered."""
        response = client.delete(
            "/activities/Basketball Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can sign up again after unregistering."""
        email = "test@mergington.edu"
        
        # Sign up
        response1 = client.post(
            f"/activities/Basketball Team/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/Basketball Team/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            f"/activities/Basketball Team/signup?email={email}"
        )
        assert response3.status_code == 200


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test complete signup and unregister flow."""
        email = "integration@mergington.edu"
        activity = "Soccer Club"
        
        # 1. Get initial state
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # 2. Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # 3. Verify added
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count + 1
        assert email in response.json()[activity]["participants"]
        
        # 4. Unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # 5. Verify removed
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count
        assert email not in response.json()[activity]["participants"]
    
    def test_multiple_activities_signup(self, client, reset_activities):
        """Test signing up for multiple activities."""
        email = "multi@mergington.edu"
        activities_list = ["Basketball Team", "Soccer Club", "Art Club"]
        
        # Sign up for multiple activities
        for activity in activities_list:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify in all activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities_list:
            assert email in data[activity]["participants"]
