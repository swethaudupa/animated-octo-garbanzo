"""
Pytest configuration and fixtures for the Activities Management System tests.

This module provides fixtures for testing the FastAPI application, including
a TestClient instance and activity data initialization/reset functionality.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient instance for making requests to the app.
    
    Returns:
        TestClient: A test client configured for the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Resets the activities database to a known state before each test.
    
    This fixture automatically runs before each test function to ensure
    test isolation and prevent test pollution from participant changes.
    Runs automatically (autouse=True) for all tests in this session.
    """
    # Clear and reinitialize activities with fresh data
    activities.clear()
    
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Train for competitive soccer matches and team play",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["nina@mergington.edu", "jack@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and scrimmage with peers",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["liam@mergington.edu", "maria@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Collaborate on instrumental and vocal music performances",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Create visual art projects using a variety of media",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore experiments, science topics, and STEM challenges",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["oliver@mergington.edu", "emma@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking skills and compete in debate tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["charlotte@mergington.edu", "ethan@mergington.edu"]
        }
    })
    
    yield
    
    # Cleanup after test (optional, but good practice)
    activities.clear()
