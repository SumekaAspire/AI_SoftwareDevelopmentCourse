"""Pytest configuration and fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient
from sys import path
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
path.insert(0, str(src_path))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store original state
    original_state = {
        "Basketball Team": {
            "description": "Join the basketball team and compete in local tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Practice soccer skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art techniques and create projects",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Drama Club": {
            "description": "Participate in theater productions and improve acting skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Team": {
            "description": "Engage in debates and improve public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Math Club": {
            "description": "Solve challenging math problems and participate in competitions",
            "schedule": "Tuesdays, 3:00 PM - 4:30 PM",
            "max_participants": 15,
            "participants": []
        },
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
        }
    }
    
    # Clear current activities
    activities.clear()
    
    # Restore original state
    activities.update(original_state)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_state)
