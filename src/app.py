"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Activity categories
activity_categories = {
    "Chess Club": "Sports",
    "Programming Class": "STEM",
    "Gym Class": "Sports",
    "Soccer Team": "Sports",
    "Swimming Club": "Sports",
    "Art Club": "Arts",
    "Drama Club": "Arts",
    "Debate Team": "Academic",
    "Science Olympiad": "STEM",
    "Book Club": "Arts"
}

# In-memory activity database
activities = {
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
        "description": "Join the varsity soccer team and compete against other schools",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Practice swimming techniques and compete in swim meets",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "ava@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art mediums including painting, drawing, and sculpture",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["lily@mergington.edu", "noah@mergington.edu"]
    },
    "Drama Club": {
        "description": "Participate in theater productions and improve acting skills",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["isabella@mergington.edu", "james@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop critical thinking and public speaking through competitive debates",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["alexander@mergington.edu", "charlotte@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Compete in science and engineering challenges at regional competitions",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["william@mergington.edu", "amelia@mergington.edu"]
    },
    "Book Club": {
        "description": "Read and discuss classic and contemporary literature",
        "schedule": "Fridays, 3:00 PM - 4:30 PM",
        "max_participants": 15,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


def get_student_activities(email: str):
    """Get all activities a student is enrolled in"""
    enrolled_activities = []
    for activity_name, activity_data in activities.items():
        if email in activity_data["participants"]:
            enrolled_activities.append(activity_name)
    return enrolled_activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")
    
    # Check if student is enrolled in 3 or more activities
    enrolled_activities = get_student_activities(email)
    if len(enrolled_activities) >= 3:
        raise HTTPException(
            status_code=400, 
            detail=f"Student is already enrolled in 3 activities. Cannot enroll in more than 3 programs."
        )
    
    # Check if student is already enrolled in an activity of the same category
    new_category = activity_categories[activity_name]
    for enrolled_activity in enrolled_activities:
        enrolled_category = activity_categories[enrolled_activity]
        if enrolled_category == new_category:
            raise HTTPException(
                status_code=400,
                detail=f"Student is already enrolled in '{enrolled_activity}' which is in the same category ({new_category}). Cannot enroll in multiple programs of the same type."
            )
    
    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/remove")
def remove_from_activity(activity_name: str, email: str):
    """Remove a participant from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
    
    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Removed {email} from {activity_name}"}

    @app.middleware("http")
    async def add_cache_control_headers(request, call_next):
        """Add cache control headers to prevent stale content"""
        response = await call_next(request)
        
        # Disable caching for API endpoints and static files
        if request.url.path.startswith("/static/") or request.url.path.startswith("/activities"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response