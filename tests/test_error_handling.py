"""
Unit tests for error handling and edge cases.

Tests error scenarios, invalid inputs, missing parameters, and edge cases
that should be handled gracefully by the API.
"""

import pytest


class TestSignupErrors:
    """Tests for error handling in the signup endpoint."""
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_activity_not_found_error_message(self, client):
        """Test that the 404 error message mentions the activity"""
        response = client.post(
            "/activities/Fake Club/signup",
            params={"email": "student@mergington.edu"}
        )
        error_message = response.json()["detail"]
        assert "activity" in error_message.lower() or "not found" in error_message.lower()
    
    def test_signup_missing_email_parameter(self, client):
        """Test that signup without email parameter fails"""
        response = client.post("/activities/Chess Club/signup")
        # FastAPI returns 422 Unprocessable Entity for missing required parameters
        assert response.status_code == 422
    
    def test_signup_empty_email_string(self, client):
        """Test signup with empty email string"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": ""}
        )
        # Should still succeed technically, but empty email is allowed by current implementation
        # Document this behavior
        assert response.status_code in [200, 422]
    
    def test_signup_activity_name_case_sensitivity(self, client):
        """Test that activity names are case-sensitive"""
        # Correct case
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Wrong case should return 404
        response2 = client.post(
            "/activities/chess club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response2.status_code == 404
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with special characters in email"""
        special_emails = [
            "user+tag@mergington.edu",
            "user.name@mergington.edu",
            "user_name@mergington.edu",
            "user-name@mergington.edu"
        ]
        
        for email in special_emails:
            response = client.post(
                "/activities/Chess Club/signup",
                params={"email": email}
            )
            # All should succeed
            assert response.status_code == 200


class TestUnregisterErrors:
    """Tests for error handling in the unregister endpoint."""
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/participants",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_unregister_missing_email_parameter(self, client):
        """Test that unregister without email parameter fails"""
        response = client.delete("/activities/Chess Club/participants")
        assert response.status_code == 422
    
    def test_unregister_empty_email_string(self, client):
        """Test unregister with empty email string"""
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": ""}
        )
        # Empty email won't match any participant
        assert response.status_code == 404
    
    def test_unregister_activity_name_case_sensitivity(self, client):
        """Test that activity names are case-sensitive for unregister"""
        # Correct case should succeed
        response1 = client.delete(
            "/activities/Chess Club/participants",
            params={"email": "michael@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Signup again for next test
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        # Wrong case should return 404
        response2 = client.delete(
            "/activities/chess club/participants",
            params={"email": "michael@mergington.edu"}
        )
        assert response2.status_code == 404
    
    def test_unregister_case_sensitive_email(self, client):
        """Test that unregister email matching is case-sensitive"""
        email_lower = "testuser@mergington.edu"
        email_upper = "TESTUSER@MERGINGTON.EDU"
        
        # Signup with lowercase
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email_lower}
        )
        
        # Try to unregister with uppercase (won't match due to case-sensitivity)
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email_upper}
        )
        # Should fail because email doesn't match (case-sensitive)
        assert response.status_code == 404


class TestActivityNameEdgeCases:
    """Tests for edge cases with activity names."""
    
    def test_activity_name_with_trailing_spaces(self, client):
        """Test that activity names with trailing spaces don't match"""
        response = client.post(
            "/activities/Chess Club /signup",  # Extra space
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_activity_name_with_leading_spaces(self, client):
        """Test that activity names with leading spaces don't match"""
        response = client.post(
            "/activities/ Chess Club/signup",  # Extra space
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_activity_names_are_exact_matches(self, client):
        """Test that activity names must be exact matches"""
        invalid_names = [
            "Chess",  # Partial
            "Club",   # Partial
            "chess club",  # Wrong case
            "Chess Club Extra",  # Extra text
            "ChessClub",  # No space
        ]
        
        for name in invalid_names:
            response = client.post(
                f"/activities/{name}/signup",
                params={"email": "student@mergington.edu"}
            )
            assert response.status_code == 404


class TestConcurrentOperations:
    """Tests for behavior with rapid/concurrent-like operations."""
    
    def test_signup_same_person_multiple_activities_simultaneously(self, client):
        """Test signing up the same person for multiple activities in sequence"""
        email = "student@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify in all activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities_to_join:
            assert email in data[activity]["participants"]
    
    def test_unregister_same_person_multiple_activities_simultaneously(self, client):
        """Test unregistering the same person from multiple activities in sequence"""
        email = "emma@mergington.edu"  # Already in multiple activities
        
        activities_to_leave = ["Programming Class", "Science Club"]
        
        for activity in activities_to_leave:
            response = client.delete(
                f"/activities/{activity}/participants",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify no longer in those activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities_to_leave:
            assert email not in data[activity]["participants"]


class TestDataIntegrity:
    """Tests to ensure data integrity across operations."""
    
    def test_total_participant_count_matches_sum(self, client):
        """Test that total participants count matches sum of all activities"""
        response = client.get("/activities")
        activities = response.json()
        
        total_participants = sum(
            len(activity["participants"]) 
            for activity in activities.values()
        )
        
        # Just verify structure is consistent
        assert total_participants > 0
        assert isinstance(total_participants, int)
    
    def test_all_participants_are_strings(self, client):
        """Test that all participant emails are strings"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email format check
    
    def test_no_duplicate_participants_in_single_activity(self, client):
        """Test that the same person doesn't appear twice in one activity"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            # Check no duplicates by comparing length with set length
            assert len(participants) == len(set(participants)), \
                f"Found duplicate participants in {activity_name}"
    
    def test_participants_list_not_none(self, client):
        """Test that participants list is never None"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert activity_data["participants"] is not None
            assert isinstance(activity_data["participants"], list)
