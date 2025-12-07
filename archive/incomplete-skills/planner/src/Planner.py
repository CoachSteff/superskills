"""
Planner.py - Outlook Calendar Integration using Microsoft Graph API.
"""
import os
from typing import Dict, List, Optional, Literal
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False
    print("Warning: msal not available - install with: pip install msal")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available - install with: pip install requests")


@dataclass
class CalendarEvent:
    """Result from a calendar operation."""
    event_id: str
    subject: str
    start_time: str
    end_time: str
    attendees: List[str]
    location: str = ""
    body: str = ""
    is_online_meeting: bool = False
    meeting_url: str = ""
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class Planner:
    """Outlook Calendar Integration using Microsoft Graph API."""
    
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    AUTHORITY = "https://login.microsoftonline.com"
    SCOPES = ["https://graph.microsoft.com/.default"]
    
    def __init__(
        self,
        output_dir: str = "output/calendar",
        verbose: bool = True
    ):
        """Initialize Planner.
        
        Args:
            output_dir: Directory to save calendar exports
            verbose: Enable verbose logging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        if not MSAL_AVAILABLE:
            raise ImportError("msal is required. Install with: pip install msal")
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests is required. Install with: pip install requests")
        
        # Validate environment variables
        self.client_id = os.getenv("MICROSOFT_CLIENT_ID")
        self.client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        self.tenant_id = os.getenv("MICROSOFT_TENANT_ID")
        
        if not self.client_id:
            raise ValueError("MICROSOFT_CLIENT_ID environment variable not set")
        if not self.client_secret:
            raise ValueError("MICROSOFT_CLIENT_SECRET environment variable not set")
        if not self.tenant_id:
            raise ValueError("MICROSOFT_TENANT_ID environment variable not set")
        
        # Initialize MSAL confidential client
        authority_url = f"{self.AUTHORITY}/{self.tenant_id}"
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority_url,
            client_credential=self.client_secret
        )
        
        self.access_token = None
    
    def _get_access_token(self) -> str:
        """Get access token for Microsoft Graph API."""
        if self.access_token:
            return self.access_token
        
        result = self.app.acquire_token_silent(self.SCOPES, account=None)
        if not result:
            result = self.app.acquire_token_for_client(scopes=self.SCOPES)
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            return self.access_token
        else:
            error = result.get("error_description", "Unknown error")
            raise RuntimeError(f"Failed to acquire token: {error}")
    
    def _make_graph_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """Make request to Microsoft Graph API."""
        token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.GRAPH_API_ENDPOINT}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code not in [200, 201, 204]:
            raise RuntimeError(f"Graph API error: {response.status_code} - {response.text}")
        
        return response.json() if response.text else {}
    
    def create_event(
        self,
        subject: str,
        start_time: datetime,
        end_time: datetime,
        attendees: Optional[List[str]] = None,
        location: str = "",
        body: str = "",
        is_online_meeting: bool = False,
        user_email: Optional[str] = None
    ) -> CalendarEvent:
        """Create a calendar event.
        
        Args:
            subject: Event subject/title
            start_time: Event start datetime
            end_time: Event end datetime
            attendees: List of attendee email addresses
            location: Event location
            body: Event description
            is_online_meeting: Create as Teams online meeting
            user_email: User's email (if None, uses default calendar)
            
        Returns:
            CalendarEvent with created event details
        """
        if self.verbose:
            print(f"Creating event: {subject}")
        
        attendee_list = []
        if attendees:
            attendee_list = [
                {
                    "emailAddress": {"address": email},
                    "type": "required"
                }
                for email in attendees
            ]
        
        event_data = {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            },
            "location": {
                "displayName": location
            },
            "attendees": attendee_list,
            "isOnlineMeeting": is_online_meeting
        }
        
        endpoint = "/me/events" if not user_email else f"/users/{user_email}/events"
        result = self._make_graph_request("POST", endpoint, event_data)
        
        meeting_url = ""
        if is_online_meeting and "onlineMeeting" in result:
            meeting_url = result["onlineMeeting"].get("joinUrl", "")
        
        event = CalendarEvent(
            event_id=result["id"],
            subject=result["subject"],
            start_time=result["start"]["dateTime"],
            end_time=result["end"]["dateTime"],
            attendees=attendees or [],
            location=location,
            body=body,
            is_online_meeting=is_online_meeting,
            meeting_url=meeting_url
        )
        
        if self.verbose:
            print(f"✓ Event created: {event.subject} at {event.start_time}")
        
        return event
    
    def find_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60,
        user_email: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Find available time slots in calendar.
        
        Args:
            start_date: Search start datetime
            end_date: Search end datetime
            duration_minutes: Required slot duration in minutes
            user_email: User's email (if None, uses default calendar)
            
        Returns:
            List of available slot dicts with 'start' and 'end' times
        """
        if self.verbose:
            print(f"Finding {duration_minutes}min slots between {start_date} and {end_date}")
        
        # Get all events in the time range
        endpoint = "/me/calendarview" if not user_email else f"/users/{user_email}/calendarview"
        params = f"?startDateTime={start_date.isoformat()}&endDateTime={end_date.isoformat()}"
        
        result = self._make_graph_request("GET", endpoint + params)
        events = result.get("value", [])
        
        # Build busy periods
        busy_periods = []
        for event in events:
            busy_periods.append({
                "start": datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00")),
                "end": datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))
            })
        
        # Sort busy periods
        busy_periods.sort(key=lambda x: x["start"])
        
        # Find free slots
        free_slots = []
        current_time = start_date
        slot_duration = timedelta(minutes=duration_minutes)
        
        for busy in busy_periods:
            while current_time + slot_duration <= busy["start"]:
                free_slots.append({
                    "start": current_time.isoformat(),
                    "end": (current_time + slot_duration).isoformat()
                })
                current_time += timedelta(hours=1)
            current_time = max(current_time, busy["end"])
        
        # Add remaining slots after last busy period
        while current_time + slot_duration <= end_date:
            free_slots.append({
                "start": current_time.isoformat(),
                "end": (current_time + slot_duration).isoformat()
            })
            current_time += timedelta(hours=1)
        
        if self.verbose:
            print(f"✓ Found {len(free_slots)} available slots")
        
        return free_slots
    
    def schedule_session(
        self,
        subject: str,
        duration_minutes: int = 60,
        attendees: Optional[List[str]] = None,
        preferred_date: Optional[datetime] = None,
        user_email: Optional[str] = None
    ) -> CalendarEvent:
        """Schedule a session in the next available slot.
        
        Args:
            subject: Event subject
            duration_minutes: Session duration in minutes
            attendees: List of attendee emails
            preferred_date: Preferred date (searches from this date)
            user_email: User's email
            
        Returns:
            CalendarEvent with scheduled session
        """
        start_search = preferred_date or datetime.now()
        end_search = start_search + timedelta(days=7)
        
        slots = self.find_available_slots(
            start_search,
            end_search,
            duration_minutes,
            user_email
        )
        
        if not slots:
            raise RuntimeError("No available slots found in the next 7 days")
        
        first_slot = slots[0]
        start_time = datetime.fromisoformat(first_slot["start"])
        end_time = datetime.fromisoformat(first_slot["end"])
        
        return self.create_event(
            subject=subject,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            is_online_meeting=True,
            user_email=user_email
        )
    
    def cancel_event(
        self,
        event_id: str,
        user_email: Optional[str] = None
    ) -> bool:
        """Cancel/delete a calendar event.
        
        Args:
            event_id: Event ID to cancel
            user_email: User's email
            
        Returns:
            True if successful
        """
        if self.verbose:
            print(f"Cancelling event: {event_id}")
        
        endpoint = f"/me/events/{event_id}" if not user_email else f"/users/{user_email}/events/{event_id}"
        self._make_graph_request("DELETE", endpoint)
        
        if self.verbose:
            print(f"✓ Event cancelled")
        
        return True
    
    def get_upcoming_events(
        self,
        days: int = 7,
        user_email: Optional[str] = None
    ) -> List[CalendarEvent]:
        """Get upcoming calendar events.
        
        Args:
            days: Number of days to look ahead
            user_email: User's email
            
        Returns:
            List of CalendarEvent objects
        """
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        if self.verbose:
            print(f"Fetching events for next {days} days")
        
        endpoint = "/me/calendarview" if not user_email else f"/users/{user_email}/calendarview"
        params = f"?startDateTime={start_date.isoformat()}&endDateTime={end_date.isoformat()}"
        
        result = self._make_graph_request("GET", endpoint + params)
        events_data = result.get("value", [])
        
        events = []
        for event_data in events_data:
            attendee_emails = [
                att["emailAddress"]["address"]
                for att in event_data.get("attendees", [])
            ]
            
            meeting_url = ""
            if event_data.get("isOnlineMeeting") and "onlineMeeting" in event_data:
                meeting_url = event_data["onlineMeeting"].get("joinUrl", "")
            
            events.append(CalendarEvent(
                event_id=event_data["id"],
                subject=event_data["subject"],
                start_time=event_data["start"]["dateTime"],
                end_time=event_data["end"]["dateTime"],
                attendees=attendee_emails,
                location=event_data.get("location", {}).get("displayName", ""),
                body=event_data.get("body", {}).get("content", ""),
                is_online_meeting=event_data.get("isOnlineMeeting", False),
                meeting_url=meeting_url
            ))
        
        if self.verbose:
            print(f"✓ Found {len(events)} upcoming events")
        
        # Save to file
        self._save_events(events)
        
        return events
    
    def block_time(
        self,
        subject: str,
        start_time: datetime,
        end_time: datetime,
        user_email: Optional[str] = None
    ) -> CalendarEvent:
        """Block time on calendar (no attendees).
        
        Args:
            subject: Block subject (e.g., "Focus Time")
            start_time: Block start datetime
            end_time: Block end datetime
            user_email: User's email
            
        Returns:
            CalendarEvent with blocked time
        """
        return self.create_event(
            subject=subject,
            start_time=start_time,
            end_time=end_time,
            attendees=None,
            body="Blocked time",
            is_online_meeting=False,
            user_email=user_email
        )
    
    def _save_events(self, events: List[CalendarEvent]):
        """Save events to JSON file."""
        output_file = self.output_dir / f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        events_data = []
        for event in events:
            events_data.append({
                "event_id": event.event_id,
                "subject": event.subject,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "attendees": event.attendees,
                "location": event.location,
                "is_online_meeting": event.is_online_meeting,
                "meeting_url": event.meeting_url
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"✓ Events saved to: {output_file}")


def create_calendar_event(
    subject: str,
    start_time: datetime,
    end_time: datetime,
    **kwargs
) -> CalendarEvent:
    """Convenience function to create a calendar event.
    
    Args:
        subject: Event subject
        start_time: Event start datetime
        end_time: Event end datetime
        **kwargs: Additional arguments for Planner
        
    Returns:
        CalendarEvent
    """
    planner = Planner()
    return planner.create_event(subject, start_time, end_time, **kwargs)
