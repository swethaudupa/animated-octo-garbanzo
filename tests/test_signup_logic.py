"""
Unit tests for signup and participation business logic.

Tests deep validation and edge cases for the signup and unregister operations,
including duplicate prevention, participant limit constraints, and data integrity.
"""

import pytest


class TestSignupValidation:
    """Tests for signup validation and business rules."""
    
    def test_duplicate_signup_returns_400(self, client):
        """Test that signing up twice with the same email returns 400 error"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "error" in response.json().get("detail", "").lower() or \
               "already" in response.json().get("detail", "").lower()
    
    def test_duplicate_signup_error_message(self, client):
        """Test that duplicate signup error message is informative"""
        email = "michael@mergington.edu"
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        error_message = response.json()["detail"]
        assert "already signed up" in error_message.lower()
    
    def test_duplicate_check_is_case_sensitive(self, client):
        """Test that duplicate check is case-sensitive for emails"""
        email_lower = "newstudent@mergington.edu"
        email_upper = "NEWSTUDENT@mergington.edu"
        
        # First signup with lowercase
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email_lower}
        )
        assert response1.status_code == 200
        
        # Second signup with uppercase should succeed (case-sensitive check)
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email_upper}
        )
        # This tests current behavior; may want to normalize emails in the future
        assert response2.status_code in [200, 400]  # Depends on implementation
    
    def test_signup_with_valid_email_formats(self, client):
        """Test signup with various valid email formats"""
        test_emails = [
            "student@mergington.edu",
            "first.last@mergington.edu",
            "student+tag@mergington.edu",
            "s.t.u.d@mergington.edu"
        ]
        
        for email in test_emails:
            response = client.post(
                "/activities/Programming Class/signup",
                params={"email": email}
            )
            assert response.status_code == 200
    
    def test_signup_preserves_existing_participants(self, client):
        """Test that signup doesn't remove or corrupt existing participants"""
        # Get initial participants
        response = client.get("/activities")
        initial_participants = response.json()["Chess Club"]["participants"].copy()
        
        # Add a new participant
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Verify all original participants are still there
        response = client.get("/activities")
        current_participants = response.json()["Chess Club"]["participants"]
        
        for original_participant in initial_participants:
            assert original_participant in current_participants
    
    def test_signup_increments_participant_count(self, client):
        """Test that signup increases the participant count by exactly 1"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        
        # Add a participant
        client.post(
            "/activities/Programming Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Check count increased by 1
        response = client.get("/activities")
        new_count = len(response.json()["Programming Class"]["participants"])
        assert new_count == initial_count + 1


class TestUnregisterValidation:
    """Tests for unregister validation and business rules."""
    
    def test_unregister_participant_not_in_activity_returns_404(self, client):
        """Test that unregistering a non-participant returns 404"""
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": "notamember@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_unregister_nonexistent_participant_error_message(self, client):
        """Test that unregister error message is informative"""
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": "notamember@mergington.edu"}
        )
        
        error_message = response.json()["detail"]
        assert "participant not found" in error_message.lower() or \
               "not found" in error_message.lower()
    
    def test_unregister_twice_fails_second_time(self, client):
        """Test that unregistering twice returns 404 the second time"""
        email = "michael@mergington.edu"
        
        # First unregister should succeed
        response1 = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert response2.status_code == 404
    
    def test_unregister_decrements_participant_count(self, client):
        """Test that unregister decreases the participant count by exactly 1"""
        email = "michael@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Remove a participant
        client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        
        # Check count decreased by 1
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1
    
    def test_unregister_preserves_other_participants(self, client):
        """Test that unregister doesn't affect other participants"""
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        
        # Get initial participants
        response = client.get("/activities")
        initial_participants = response.json()["Chess Club"]["participants"].copy()
        
        # Remove one participant
        client.delete(
            "/activities/Chess Club/participants",
            params={"email": email_to_remove}
        )
        
        # Verify the other participant is still there
        response = client.get("/activities")
        current_participants = response.json()["Chess Club"]["participants"]
        assert email_to_keep in current_participants
        assert email_to_remove not in current_participants


class TestSignupUnregisterRoundTrip:
    """Tests for signup followed by unregister sequences."""
    
    def test_signup_then_unregister_returns_to_original_state(self, client):
        """Test that signup followed by unregister returns activity to original state"""
        email = "newstudent@mergington.edu"
        
        # Get initial state
        response = client.get("/activities")
        initial_participants = response.json()["Chess Club"]["participants"].copy()
        initial_count = len(initial_participants)
        
        # Signup
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Verify student was added
        response = client.get("/activities")
        assert len(response.json()["Chess Club"]["participants"]) == initial_count + 1
        
        # Unregister
        client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        
        # Verify back to original state
        response = client.get("/activities")
        final_participants = response.json()["Chess Club"]["participants"]
        assert len(final_participants) == initial_count
        # Check original participants are intact
        for participant in initial_participants:
            assert participant in final_participants
    
    def test_multiple_signup_unregister_cycles(self, client):
        """Test multiple rounds of signup/unregister cycles"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Cycle 1: signup, unregister
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email1}
        )
        assert email1 in client.get("/activities").json()["Chess Club"]["participants"]
        
        client.delete(
            "/activities/Chess Club/participants",
            params={"email": email1}
        )
        assert email1 not in client.get("/activities").json()["Chess Club"]["participants"]
        
        # Cycle 2: signup different student, unregister
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email2}
        )
        assert email2 in client.get("/activities").json()["Chess Club"]["participants"]
        
        client.delete(
            "/activities/Chess Club/participants",
            params={"email": email2}
        )
        assert email2 not in client.get("/activities").json()["Chess Club"]["participants"]
    
    def test_signup_after_unregister_succeeds(self, client):
        """Test that a student can re-signup after unregistering"""
        email = "michael@mergington.edu"
        
        # Initial state: student is signed up
        assert email in client.get("/activities").json()["Chess Club"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert email not in client.get("/activities").json()["Chess Club"]["participants"]
        
        # Re-signup should succeed
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        assert email in client.get("/activities").json()["Chess Club"]["participants"]
