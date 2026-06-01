"""
Unit tests for all main API endpoints.

Tests the four main endpoints of the Activities Management System:
- GET / (redirect to static page)
- GET /activities (retrieve all activities)
- POST /activities/{activity_name}/signup (sign up a student)
- DELETE /activities/{activity_name}/participants (unregister a student)
"""

import pytest


class TestRootEndpoint:
    """Tests for the GET / endpoint."""
    
    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""
    
    def test_get_all_activities_returns_200(self, client):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_all_nine_activities(self, client):
        """Test that all 9 activities are returned"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) == 9
    
    def test_get_activities_contains_expected_activity_names(self, client):
        """Test that the response contains all expected activity names"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Basketball Club",
            "Music Ensemble",
            "Art Studio",
            "Science Club",
            "Debate Team"
        ]
        
        for activity_name in expected_activities:
            assert activity_name in activities
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields
    
    def test_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
    
    def test_max_participants_is_integer(self, client):
        """Test that max_participants field is an integer"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_successful_signup(self, client):
        """Test a successful signup for a student"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Signed up" in response.json()["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the student to the activity"""
        email = "newstudent@mergington.edu"
        
        # Signup
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_different_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "student@mergington.edu"
        
        # Sign up for two different activities
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify in both activities
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_returns_activity_name_in_message(self, client):
        """Test that the response message includes the activity name"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert "Chess Club" in response.json()["message"]
    
    def test_signup_returns_email_in_message(self, client):
        """Test that the response message includes the email"""
        email = "test@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert email in response.json()["message"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_successful_unregister(self, client):
        """Test successfully unregistering a student from an activity"""
        email = "michael@mergington.edu"  # This student is in Chess Club
        
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the student from the activity"""
        email = "michael@mergington.edu"
        
        # Verify student is in the activity
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        
        # Verify student was removed
        response = client.get("/activities")
        assert email not in response.json()["Chess Club"]["participants"]
    
    def test_unregister_returns_activity_name_in_message(self, client):
        """Test that the response message includes the activity name"""
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": "michael@mergington.edu"}
        )
        assert "Chess Club" in response.json()["message"]
    
    def test_unregister_returns_email_in_message(self, client):
        """Test that the response message includes the email"""
        email = "michael@mergington.edu"
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert email in response.json()["message"]
    
    def test_unregister_multiple_times_from_different_activities(self, client):
        """Test unregistering from multiple different activities"""
        email1 = "michael@mergington.edu"  # In Chess Club
        email2 = "emma@mergington.edu"      # In Programming Class and Science Club
        
        # Unregister from different activities
        response1 = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email1}
        )
        response2 = client.delete(
            "/activities/Programming Class/participants",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify they were removed
        response = client.get("/activities")
        activities = response.json()
        assert email1 not in activities["Chess Club"]["participants"]
        assert email2 not in activities["Programming Class"]["participants"]
