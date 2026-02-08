"""
Test suite for the Mergington High School API.
"""
import pytest


class TestRootEndpoint:
    """Test the root endpoint."""
    
    def test_root_redirect(self, client):
        """Test that the root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we have all expected activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Tennis Team" in data
        assert "Basketball League" in data
        assert "Debate Club" in data
        assert "Science Olympiad" in data
        assert "Art Studio" in data
        assert "Drama Club" in data
    
    def test_activity_contains_required_fields(self, client, reset_activities):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_activity_has_initial_participants(self, client, reset_activities):
        """Test that activities have initial participants."""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have initial participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupEndpoint:
    """Test the signup endpoint."""
    
    def test_signup_for_existing_activity(self, client, reset_activities):
        """Test signing up for an existing activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    
    def test_signup_verification(self, client, reset_activities):
        """Test that a student is actually added after signup."""
        # Sign up the student
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # Verify the student is in the participants list
        response = client.get("/activities")
        activities = response.json()
        assert "test@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test that signup for a non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_duplicate_signup(self, client, reset_activities):
        """Test that signing up twice for the same activity fails."""
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup?email=duplicate@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Duplicate signup
        response2 = client.post(
            "/activities/Chess Club/signup?email=duplicate@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_for_activity_with_existing_participants(self, client, reset_activities):
        """Test that existing participants aren't affected by new signup."""
        # Sign up a new student
        client.post("/activities/Chess Club/signup?email=new@mergington.edu")
        
        # Verify original participants are still there
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" in participants
        assert "daniel@mergington.edu" in participants
        assert "new@mergington.edu" in participants


class TestUnregisterEndpoint:
    """Test the unregister endpoint."""
    
    def test_unregister_from_activity(self, client, reset_activities):
        """Test unregistering from an activity."""
        # First, sign up a student
        client.post("/activities/Chess Club/signup?email=unreg@mergington.edu")
        
        # Then unregister
        response = client.post(
            "/activities/Chess Club/unregister?email=unreg@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unregistered unreg@mergington.edu from Chess Club"
    
    def test_unregister_verification(self, client, reset_activities):
        """Test that a student is actually removed after unregister."""
        # Sign up then unregister
        client.post("/activities/Chess Club/signup?email=temp@mergington.edu")
        client.post("/activities/Chess Club/unregister?email=temp@mergington.edu")
        
        # Verify the student is removed
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert "temp@mergington.edu" not in participants
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test that unregister from a non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test that unregistering a student who isn't signed up fails."""
        response = client.post(
            "/activities/Chess Club/unregister?email=notsignup@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_from_activity_with_original_participants(self, client, reset_activities):
        """Test that unregistering one participant doesn't affect others."""
        # Unregister an original participant
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify the other participant is still there
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in participants
        assert "michael@mergington.edu" not in participants
