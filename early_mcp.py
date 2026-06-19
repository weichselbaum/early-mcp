#!/usr/bin/env python3
"""Early (Timeular) MCP Server - Complete time tracking integration."""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# Initialize MCP server
mcp = FastMCP("early")

# Configuration
BASE_URL = "https://api.early.app/api/v4"
API_KEY = os.environ.get("EARLY_API_KEY", "")
API_SECRET = os.environ.get("EARLY_API_SECRET", "")

# Token cache
_token_cache = {"token": None, "expires": None}


async def get_token() -> str:
    """Get or refresh authentication token."""
    if not API_KEY or not API_SECRET:
        raise ValueError("EARLY_API_KEY and EARLY_API_SECRET environment variables required")
    
    now = datetime.now()
    if _token_cache["token"] and _token_cache["expires"] and _token_cache["expires"] > now:
        return _token_cache["token"]
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/developer/sign-in",
            json={"apiKey": API_KEY, "apiSecret": API_SECRET},
            timeout=30.0
        )
        resp.raise_for_status()
        token = resp.json()["token"]
        _token_cache["token"] = token
        _token_cache["expires"] = now + timedelta(hours=1)
        return token


async def api_request(method: str, endpoint: str, json_data: dict = None) -> dict:
    """Make authenticated API request."""
    token = await get_token()
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method,
            f"{BASE_URL}{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            json=json_data,
            timeout=30.0
        )
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return {"success": True}
        return resp.json()


def format_duration(start: str, stop: str) -> str:
    """Format duration between two ISO timestamps."""
    try:
        s = datetime.fromisoformat(start.replace("Z", "+00:00").split(".")[0])
        e = datetime.fromisoformat(stop.replace("Z", "+00:00").split(".")[0])
        delta = e - s
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes = remainder // 60
        return f"{hours}h {minutes}m"
    except:
        return "?"


def handle_error(e: Exception) -> str:
    """Format API errors."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        try:
            msg = e.response.json().get("message", str(e))
        except:
            msg = str(e)
        return f"Error {status}: {msg}"
    return f"Error: {str(e)}"


# ============ Input Models ============

class EmptyInput(BaseModel):
    """No parameters required."""
    model_config = ConfigDict(extra='forbid')


class ActivityIdInput(BaseModel):
    """Activity ID parameter."""
    model_config = ConfigDict(extra='forbid')
    activity_id: str = Field(..., description="Activity ID")


class TimeEntryIdInput(BaseModel):
    """Time entry ID parameter."""
    model_config = ConfigDict(extra='forbid')
    time_entry_id: str = Field(..., description="Time entry ID")


class StartTrackingInput(BaseModel):
    """Start tracking parameters."""
    model_config = ConfigDict(extra='forbid')
    activity_id: str = Field(..., description="Activity ID to track")
    started_at: Optional[str] = Field(default=None, description="Start time (ISO 8601). Defaults to now.")


class StopTrackingInput(BaseModel):
    """Stop tracking parameters."""
    model_config = ConfigDict(extra='forbid')
    stopped_at: Optional[str] = Field(default=None, description="Stop time (ISO 8601). Defaults to now.")


class EditTrackingInput(BaseModel):
    """Edit current tracking parameters."""
    model_config = ConfigDict(extra='forbid')
    note: Optional[str] = Field(default=None, description="Note text (use <{{|t|ID|}}> for tags, <{{|m|ID|}}> for mentions)")
    activity_id: Optional[str] = Field(default=None, description="Change activity")
    started_at: Optional[str] = Field(default=None, description="Change start time (ISO 8601)")


class TimeRangeInput(BaseModel):
    """Time range parameters."""
    model_config = ConfigDict(extra='forbid')
    start: Optional[str] = Field(default=None, description="Start date (ISO 8601 or YYYY-MM-DD). Defaults to 7 days ago.")
    end: Optional[str] = Field(default=None, description="End date (ISO 8601 or YYYY-MM-DD). Defaults to now.")


class CreateTimeEntryInput(BaseModel):
    """Create time entry parameters."""
    model_config = ConfigDict(extra='forbid')
    activity_id: str = Field(..., description="Activity ID")
    started_at: str = Field(..., description="Start time (ISO 8601)")
    stopped_at: str = Field(..., description="Stop time (ISO 8601)")
    note: Optional[str] = Field(default=None, description="Note text")


class EditTimeEntryInput(BaseModel):
    """Edit time entry parameters."""
    model_config = ConfigDict(extra='forbid')
    time_entry_id: str = Field(..., description="Time entry ID to edit")
    activity_id: Optional[str] = Field(default=None, description="New activity ID")
    started_at: Optional[str] = Field(default=None, description="New start time (ISO 8601)")
    stopped_at: Optional[str] = Field(default=None, description="New stop time (ISO 8601)")
    note: Optional[str] = Field(default=None, description="New note text (null to remove)")


class CreateActivityInput(BaseModel):
    """Create activity parameters."""
    model_config = ConfigDict(extra='forbid')
    name: str = Field(..., description="Activity name")
    color: str = Field(default="#3498db", description="Hex color (e.g. #3498db)")
    folder_id: str = Field(..., description="Folder ID to create activity in")


class EditActivityInput(BaseModel):
    """Edit activity parameters."""
    model_config = ConfigDict(extra='forbid')
    activity_id: str = Field(..., description="Activity ID to edit")
    name: Optional[str] = Field(default=None, description="New name")
    color: Optional[str] = Field(default=None, description="New hex color")


class ReportInput(BaseModel):
    """Report generation parameters."""
    model_config = ConfigDict(extra='forbid')
    start_date: str = Field(..., description="Inclusive start date, format YYYY-MM-DD (e.g. 2024-07-01). No time component.")
    end_date: str = Field(..., description="Inclusive end date, format YYYY-MM-DD (e.g. 2024-07-31). No time component.")
    activity_ids: Optional[List[str]] = Field(default=None, description="Optional. Restrict to these activity IDs (from early_list_activities). Omit for all activities.")
    folder_ids: Optional[List[str]] = Field(default=None, description="Optional. Restrict to these folder IDs (from early_list_folders). Omit for all folders.")
    user_ids: Optional[List[str]] = Field(default=None, description="Optional. Restrict to these team member user IDs (from early_list_users). Omit to include every member you have Full folder access to. Other members' entries are only visible with Full access.")


# Tag & Mention Models
class CreateTagInput(BaseModel):
    """Create tag parameters."""
    model_config = ConfigDict(extra='forbid')
    label: str = Field(..., description="Tag label (displayed name)")
    folder_id: str = Field(..., description="Folder ID")
    key: Optional[str] = Field(default=None, description="Unique key (auto-generated if not provided)")
    scope: str = Field(default="timeular", description="Scope (default: timeular)")


class UpdateTagInput(BaseModel):
    """Update tag parameters."""
    model_config = ConfigDict(extra='forbid')
    tag_id: int = Field(..., description="Tag ID to update")
    label: str = Field(..., description="New label")


class TagIdInput(BaseModel):
    """Tag ID parameter."""
    model_config = ConfigDict(extra='forbid')
    tag_id: int = Field(..., description="Tag ID")


class CreateMentionInput(BaseModel):
    """Create mention parameters."""
    model_config = ConfigDict(extra='forbid')
    label: str = Field(..., description="Mention label (displayed name)")
    folder_id: str = Field(..., description="Folder ID")
    key: Optional[str] = Field(default=None, description="Unique key (auto-generated if not provided)")
    scope: str = Field(default="timeular", description="Scope (default: timeular)")


class UpdateMentionInput(BaseModel):
    """Update mention parameters."""
    model_config = ConfigDict(extra='forbid')
    mention_id: int = Field(..., description="Mention ID to update")
    label: str = Field(..., description="New label")


class MentionIdInput(BaseModel):
    """Mention ID parameter."""
    model_config = ConfigDict(extra='forbid')
    mention_id: int = Field(..., description="Mention ID")


# Folder Models
class FolderIdInput(BaseModel):
    """Folder ID parameter."""
    model_config = ConfigDict(extra='forbid')
    folder_id: str = Field(..., description="Folder ID")


class CreateFolderInput(BaseModel):
    """Create folder parameters."""
    model_config = ConfigDict(extra='forbid')
    name: str = Field(..., description="Folder name")
    is_workspace_folder: bool = Field(default=True, description="Whether this is a workspace folder")


class EditFolderInput(BaseModel):
    """Edit folder parameters."""
    model_config = ConfigDict(extra='forbid')
    folder_id: str = Field(..., description="Folder ID to edit")
    name: str = Field(..., description="New folder name")


class FolderMemberInput(BaseModel):
    """Folder member parameters."""
    model_config = ConfigDict(extra='forbid')
    folder_id: str = Field(..., description="Folder ID")
    user_id: str = Field(..., description="User ID")


class AddFolderMemberInput(BaseModel):
    """Add folder member parameters."""
    model_config = ConfigDict(extra='forbid')
    folder_id: str = Field(..., description="Folder ID")
    email: str = Field(..., description="Member email address")
    access_level: str = Field(default="personal", description="Access level: 'full' or 'personal'")


# Leave Models
class CreateLeaveInput(BaseModel):
    """Create leave parameters."""
    model_config = ConfigDict(extra='forbid')
    type_id: str = Field(..., description="Leave type ID")
    start_date: str = Field(..., description="Start date (ISO 8601)")
    end_date: str = Field(..., description="End date (ISO 8601)")
    note: Optional[str] = Field(default=None, description="Optional note")


class CreateLeaveForUserInput(BaseModel):
    """Create leave for user parameters."""
    model_config = ConfigDict(extra='forbid')
    user_id: str = Field(..., description="User ID")
    type_id: str = Field(..., description="Leave type ID")
    start_date: str = Field(..., description="Start date (ISO 8601)")
    end_date: str = Field(..., description="End date (ISO 8601)")
    note: Optional[str] = Field(default=None, description="Optional note")


class LeaveIdInput(BaseModel):
    """Leave ID parameter."""
    model_config = ConfigDict(extra='forbid')
    leave_id: str = Field(..., description="Leave ID")


# Webhook Models
class WebhookSubscribeInput(BaseModel):
    """Webhook subscribe parameters."""
    model_config = ConfigDict(extra='forbid')
    event: str = Field(..., description="Event to subscribe to")
    target_url: str = Field(..., description="HTTPS URL to receive webhook")


class WebhookIdInput(BaseModel):
    """Webhook ID parameter."""
    model_config = ConfigDict(extra='forbid')
    subscription_id: str = Field(..., description="Webhook subscription ID")


# ============ User & Auth Tools ============

@mcp.tool(
    name="early_get_me",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_get_me(params: EmptyInput) -> str:
    """Get current authenticated user info."""
    try:
        data = await api_request("GET", "/me")
        return f"User: {data['name']} ({data['email']})\nID: {data['id']}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_list_users",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_list_users(params: EmptyInput) -> str:
    """List all team users."""
    try:
        data = await api_request("GET", "/users")
        lines = ["## Team Users"]
        for u in data.get("users", []):
            lines.append(f"- **{u['name']}** ({u['email']}) - ID: {u['id']}")
        return "\n".join(lines) if lines else "No users found."
    except Exception as e:
        return handle_error(e)


# ============ Activity Tools ============

@mcp.tool(
    name="early_list_activities",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_list_activities(params: EmptyInput) -> str:
    """List all activities (active, inactive, archived)."""
    try:
        data = await api_request("GET", "/activities")
        lines = ["## Active Activities"]
        for a in data.get("activities", []):
            lines.append(f"- **{a['name']}** (ID: {a['id']}, Folder: {a['folderId']})")
        
        inactive = data.get("inactiveActivities", [])
        if inactive:
            lines.append("\n## Inactive Activities")
            for a in inactive:
                lines.append(f"- {a['name']} (ID: {a['id']})")
        
        archived = data.get("archivedActivities", [])
        if archived:
            lines.append("\n## Archived Activities")
            for a in archived:
                lines.append(f"- {a['name']} (ID: {a['id']})")
        
        return "\n".join(lines) if lines else "No activities found."
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_create_activity",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_create_activity(params: CreateActivityInput) -> str:
    """Create a new activity."""
    try:
        data = await api_request("POST", "/activities", {
            "name": params.name,
            "color": params.color,
            "folderId": params.folder_id
        })
        return f"Created activity: {params.name} (ID: {data.get('id', '?')})"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_edit_activity",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_edit_activity(params: EditActivityInput) -> str:
    """Edit an existing activity."""
    try:
        body = {}
        if params.name:
            body["name"] = params.name
        if params.color:
            body["color"] = params.color
        
        data = await api_request("PATCH", f"/activities/{params.activity_id}", body)
        return f"Updated activity {params.activity_id}: {data.get('name', '?')}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_archive_activity",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_archive_activity(params: ActivityIdInput) -> str:
    """Archive an activity."""
    try:
        await api_request("DELETE", f"/activities/{params.activity_id}")
        return f"Archived activity {params.activity_id}."
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_unarchive_activity",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_unarchive_activity(params: ActivityIdInput) -> str:
    """Unarchive an activity."""
    try:
        data = await api_request("POST", f"/activities/{params.activity_id}/unarchive")
        return f"Unarchived activity: {data.get('name', params.activity_id)}"
    except Exception as e:
        return handle_error(e)


# ============ Tracking Tools ============

@mcp.tool(
    name="early_get_tracking",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_get_tracking(params: EmptyInput) -> str:
    """Get current active tracking (running timer)."""
    try:
        data = await api_request("GET", "/tracking")
        if not data or "currentTracking" in data and data["currentTracking"] is None:
            return "No active tracking."
        
        activity = data.get("activity", {})
        started = data.get("startedAt", "?")
        note = data.get("note", {})
        note_text = note.get("text", "") if note else ""
        
        try:
            start_dt = datetime.fromisoformat(started.split(".")[0])
            elapsed = datetime.now() - start_dt
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes = remainder // 60
            elapsed_str = f"{hours}h {minutes}m"
        except:
            elapsed_str = "?"
        
        lines = [
            f"## Currently Tracking",
            f"**Activity:** {activity.get('name', '?')} (ID: {activity.get('id', '?')})",
            f"**Started:** {started}",
            f"**Elapsed:** {elapsed_str}",
        ]
        if note_text:
            lines.append(f"**Note:** {note_text}")
        
        return "\n".join(lines)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return "No active tracking."
        return handle_error(e)
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_start_tracking",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_start_tracking(params: StartTrackingInput) -> str:
    """Start tracking time for an activity."""
    try:
        started_at = params.started_at or datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000")
        data = await api_request(
            "POST",
            f"/tracking/{params.activity_id}/start",
            {"startedAt": started_at}
        )
        activity = data.get("activity", {})
        return f"Started tracking: {activity.get('name', params.activity_id)} at {started_at}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_stop_tracking",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_stop_tracking(params: StopTrackingInput) -> str:
    """Stop current tracking and create a time entry. Requires minimum 1 minute duration."""
    try:
        stopped_at = params.stopped_at or datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000")
        data = await api_request("POST", "/tracking/stop", {"stoppedAt": stopped_at})
        
        activity = data.get("activity", {})
        duration = data.get("duration", {})
        started = duration.get("startedAt", "?")
        stopped = duration.get("stoppedAt", "?")
        dur_str = format_duration(started, stopped)
        
        return f"Stopped tracking: {activity.get('name', '?')}\nDuration: {dur_str}\nTime Entry ID: {data.get('id', '?')}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_edit_tracking",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_edit_tracking(params: EditTrackingInput) -> str:
    """Edit the current tracking (note, activity, start time)."""
    try:
        body = {}
        if params.note is not None:
            body["note"] = {"text": params.note}
        if params.activity_id:
            body["activityId"] = params.activity_id
        if params.started_at:
            body["startedAt"] = params.started_at
        
        data = await api_request("PATCH", "/tracking", body)
        return f"Updated tracking. Activity: {data.get('activity', {}).get('name', '?')}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_cancel_tracking",
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
)
async def early_cancel_tracking(params: EmptyInput) -> str:
    """Cancel current tracking without creating a time entry."""
    try:
        await api_request("DELETE", "/tracking")
        return "Tracking cancelled. No time entry created."
    except Exception as e:
        return handle_error(e)


# ============ Time Entry Tools ============

@mcp.tool(
    name="early_list_time_entries",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_list_time_entries(params: TimeRangeInput) -> str:
    """List individual time entries in a date range for the AUTHENTICATED account only.

    This is personal-scope: it cannot return other team members' entries and does
    not accept a user filter. For team-wide data use early_generate_report
    (aggregated, supports user_ids) or early_analyze_time_distribution
    (per-user x activity breakdown). Delivers a list of entries with activity
    name, start/stop, duration, note, and entry ID, plus a total. Timestamps are
    UTC and this endpoint returns no per-entry timezone, so convert to the
    account's known local timezone before any time-of-day reasoning.
    """
    try:
        now = datetime.now()
        if params.start:
            start = params.start if "T" in params.start else f"{params.start}T00:00:00.000"
        else:
            start = (now - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00.000")
        
        if params.end:
            end = params.end if "T" in params.end else f"{params.end}T23:59:59.999"
        else:
            end = now.strftime("%Y-%m-%dT23:59:59.999")
        
        data = await api_request("GET", f"/time-entries/{start}/{end}")
        entries = data.get("timeEntries", [])
        
        if not entries:
            return f"No time entries found between {start} and {end}."
        
        lines = [
            f"## Time Entries ({start[:10]} to {end[:10]})",
            "",
            "_Timestamps are UTC (no per-entry timezone available; convert via the account's own timezone)._",
            "",
        ]
        total_seconds = 0
        
        for e in entries:
            activity = e.get("activity", {})
            duration = e.get("duration", {})
            started = duration.get("startedAt", "")
            stopped = duration.get("stoppedAt", "")
            note = e.get("note", {})
            note_text = note.get("text", "") if note else ""
            
            dur_str = format_duration(started, stopped)
            
            try:
                s = datetime.fromisoformat(started.split(".")[0])
                t = datetime.fromisoformat(stopped.split(".")[0])
                total_seconds += int((t - s).total_seconds())
            except:
                pass
            
            lines.append(f"**{activity.get('name', '?')}** - {dur_str}")
            lines.append(f"  {started[:16]} → {stopped[11:16]} UTC (ID: {e.get('id', '?')})")
            if note_text:
                lines.append(f"  Note: {note_text[:100]}")
            lines.append("")
        
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        lines.append(f"**Total: {hours}h {minutes}m**")
        
        return "\n".join(lines)
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_get_time_entry",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_get_time_entry(params: TimeEntryIdInput) -> str:
    """Get a specific time entry by ID."""
    try:
        data = await api_request("GET", f"/time-entries/{params.time_entry_id}")
        activity = data.get("activity", {})
        duration = data.get("duration", {})
        note = data.get("note", {})
        
        lines = [
            f"## Time Entry {data.get('id')}",
            f"**Activity:** {activity.get('name', '?')} (ID: {activity.get('id')})",
            f"**Started:** {duration.get('startedAt', '?')}",
            f"**Stopped:** {duration.get('stoppedAt', '?')}",
            f"**Duration:** {format_duration(duration.get('startedAt', ''), duration.get('stoppedAt', ''))}",
        ]
        if note and note.get("text"):
            lines.append(f"**Note:** {note['text']}")
        
        return "\n".join(lines)
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_create_time_entry",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_create_time_entry(params: CreateTimeEntryInput) -> str:
    """Create a new time entry. Minimum duration: 1 minute."""
    try:
        body = {
            "activityId": params.activity_id,
            "startedAt": params.started_at,
            "stoppedAt": params.stopped_at
        }
        if params.note:
            body["note"] = {"text": params.note}
        
        data = await api_request("POST", "/time-entries", body)
        return f"Created time entry. ID: {data.get('id', '?')}, Duration: {format_duration(params.started_at, params.stopped_at)}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_edit_time_entry",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_edit_time_entry(params: EditTimeEntryInput) -> str:
    """Edit an existing time entry."""
    try:
        body = {}
        if params.activity_id:
            body["activityId"] = params.activity_id
        if params.started_at:
            body["startedAt"] = params.started_at
        if params.stopped_at:
            body["stoppedAt"] = params.stopped_at
        if params.note is not None:
            body["note"] = {"text": params.note} if params.note else None
        
        data = await api_request("PATCH", f"/time-entries/{params.time_entry_id}", body)
        return f"Updated time entry {params.time_entry_id}."
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_delete_time_entry",
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
)
async def early_delete_time_entry(params: TimeEntryIdInput) -> str:
    """Delete a time entry."""
    try:
        await api_request("DELETE", f"/time-entries/{params.time_entry_id}")
        return f"Deleted time entry {params.time_entry_id}."
    except Exception as e:
        return handle_error(e)


# ============ Folder Tools ============

@mcp.tool(
    name="early_list_folders",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_list_folders(params: EmptyInput) -> str:
    """List all folders."""
    try:
        data = await api_request("GET", "/folders")
        lines = ["## Folders"]
        for f in data.get("folders", []):
            members = ", ".join([m['name'] for m in f.get('members', [])])
            lines.append(f"- **{f['name']}** (ID: {f['id']}, Status: {f['status']})")
            if members:
                lines.append(f"  Members: {members}")
        return "\n".join(lines) if lines else "No folders found."
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_get_folder",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_get_folder(params: FolderIdInput) -> str:
    """Get a specific folder by ID."""
    try:
        data = await api_request("GET", f"/folders/{params.folder_id}")
        lines = [
            f"## Folder: {data.get('name', '?')}",
            f"**ID:** {data.get('id')}",
            f"**Status:** {data.get('status', '?')}",
            "",
            "### Members"
        ]
        for m in data.get("members", []):
            lines.append(f"- {m['name']} ({m['email']}) - {m.get('accessLevel', '?')}")
        
        retired = data.get("retiredMembers", [])
        if retired:
            lines.append("\n### Retired Members")
            for m in retired:
                lines.append(f"- {m['name']}")
        
        return "\n".join(lines)
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_create_folder",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_create_folder(params: CreateFolderInput) -> str:
    """Create a new folder."""
    try:
        body = {"name": params.name}
        if not params.is_workspace_folder:
            body["isWorkspaceFolder"] = False
        
        data = await api_request("POST", "/folders", body)
        return f"Created folder: {params.name} (ID: {data.get('id', '?')})"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_edit_folder",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_edit_folder(params: EditFolderInput) -> str:
    """Edit a folder name."""
    try:
        data = await api_request("PATCH", f"/folders/{params.folder_id}", {"name": params.name})
        return f"Updated folder {params.folder_id}: {data.get('name', '?')}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_archive_folder",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_archive_folder(params: FolderIdInput) -> str:
    """Archive a folder. All activities, tags, and mentions will be archived."""
    try:
        data = await api_request("POST", f"/folders/{params.folder_id}/archive")
        return f"Archived folder: {data.get('name', params.folder_id)}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_unarchive_folder",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_unarchive_folder(params: FolderIdInput) -> str:
    """Unarchive a folder. All activities, tags, and mentions will be unarchived."""
    try:
        data = await api_request("POST", f"/folders/{params.folder_id}/unarchive")
        return f"Unarchived folder: {data.get('name', params.folder_id)}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_list_folder_members",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_list_folder_members(params: FolderIdInput) -> str:
    """List all members of a folder."""
    try:
        data = await api_request("GET", f"/folders/{params.folder_id}/members")
        lines = ["## Folder Members"]
        for m in data.get("members", []):
            lines.append(f"- **{m['name']}** ({m['email']}) - {m.get('accessLevel', '?')} (ID: {m['id']})")
        
        retired = data.get("retiredMembers", [])
        if retired:
            lines.append("\n## Retired Members")
            for m in retired:
                lines.append(f"- {m['name']} (ID: {m['id']})")
        
        return "\n".join(lines) if lines else "No members found."
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_get_folder_member",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_get_folder_member(params: FolderMemberInput) -> str:
    """Get a specific folder member."""
    try:
        data = await api_request("GET", f"/folders/{params.folder_id}/members/{params.user_id}")
        return f"**{data['name']}** ({data['email']})\nAccess Level: {data.get('accessLevel', '?')}\nID: {data['id']}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_add_folder_member",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_add_folder_member(params: AddFolderMemberInput) -> str:
    """Add a member to a folder by email."""
    try:
        data = await api_request("POST", f"/folders/{params.folder_id}/members", {
            "email": params.email,
            "accessLevel": params.access_level
        })
        status = "invited" if data.get("id") == "pending" else "added"
        return f"Member {status}: {params.email} with {params.access_level} access"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_remove_folder_member",
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
)
async def early_remove_folder_member(params: FolderMemberInput) -> str:
    """Remove a member from a folder."""
    try:
        await api_request("DELETE", f"/folders/{params.folder_id}/members/{params.user_id}")
        return f"Removed user {params.user_id} from folder {params.folder_id}."
    except Exception as e:
        return handle_error(e)


# ============ Tag Tools ============

@mcp.tool(
    name="early_list_tags",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_list_tags(params: EmptyInput) -> str:
    """List all tags and mentions."""
    try:
        data = await api_request("GET", "/tags-and-mentions")
        
        lines = ["## Tags"]
        for t in data.get("tags", []):
            lines.append(f"- #{t['label']} (ID: {t['id']}, Folder: {t.get('folderId', '?')})")
        
        mentions = data.get("mentions", [])
        if mentions:
            lines.append("\n## Mentions")
            for m in mentions:
                lines.append(f"- @{m['label']} (ID: {m['id']}, Folder: {m.get('folderId', '?')})")
        
        return "\n".join(lines) if lines else "No tags or mentions found."
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_create_tag",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_create_tag(params: CreateTagInput) -> str:
    """Create a new tag."""
    try:
        import uuid
        body = {
            "key": params.key or str(uuid.uuid4()),
            "label": params.label,
            "scope": params.scope,
            "folderId": params.folder_id
        }
        data = await api_request("POST", "/tags", body)
        return f"Created tag: #{params.label} (ID: {data.get('id', '?')})"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_update_tag",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_update_tag(params: UpdateTagInput) -> str:
    """Update a tag's label."""
    try:
        data = await api_request("PATCH", f"/tags/{params.tag_id}", {"label": params.label})
        return f"Updated tag {params.tag_id}: #{data.get('label', '?')}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_delete_tag",
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
)
async def early_delete_tag(params: TagIdInput) -> str:
    """Delete a tag. Returns affected time entries."""
    try:
        data = await api_request("DELETE", f"/tags/{params.tag_id}")
        affected = data.get("timeEntryIds", [])
        msg = f"Deleted tag {params.tag_id}."
        if affected:
            msg += f" Affected {len(affected)} time entries."
        return msg
    except Exception as e:
        return handle_error(e)


# ============ Mention Tools ============

@mcp.tool(
    name="early_create_mention",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_create_mention(params: CreateMentionInput) -> str:
    """Create a new mention."""
    try:
        import uuid
        body = {
            "key": params.key or str(uuid.uuid4()),
            "label": params.label,
            "scope": params.scope,
            "folderId": params.folder_id
        }
        data = await api_request("POST", "/mentions", body)
        return f"Created mention: @{params.label} (ID: {data.get('id', '?')})"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_update_mention",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_update_mention(params: UpdateMentionInput) -> str:
    """Update a mention's label."""
    try:
        data = await api_request("PATCH", f"/mentions/{params.mention_id}", {"label": params.label})
        return f"Updated mention {params.mention_id}: @{data.get('label', '?')}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_delete_mention",
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
)
async def early_delete_mention(params: MentionIdInput) -> str:
    """Delete a mention. Returns affected time entries."""
    try:
        data = await api_request("DELETE", f"/mentions/{params.mention_id}")
        affected = data.get("timeEntryIds", [])
        msg = f"Deleted mention {params.mention_id}."
        if affected:
            msg += f" Affected {len(affected)} time entries."
        return msg
    except Exception as e:
        return handle_error(e)


# ============ Leave Tools ============

@mcp.tool(
    name="early_create_leave",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_create_leave(params: CreateLeaveInput) -> str:
    """Create a leave request for yourself."""
    try:
        body = {
            "typeId": params.type_id,
            "startDate": params.start_date,
            "endDate": params.end_date
        }
        if params.note:
            body["note"] = params.note
        
        data = await api_request("POST", "/leaves", body)
        return f"Created leave request (ID: {data.get('id', '?')}) - Status: {data.get('status', '?')}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_create_leave_for_user",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_create_leave_for_user(params: CreateLeaveForUserInput) -> str:
    """Create an approved leave for a team member. Requires Admin/Owner role."""
    try:
        body = {
            "typeId": params.type_id,
            "startDate": params.start_date,
            "endDate": params.end_date
        }
        if params.note:
            body["note"] = params.note
        
        data = await api_request("POST", f"/users/{params.user_id}/leaves", body)
        return f"Created leave for user {params.user_id} (ID: {data.get('id', '?')})"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_approve_leave",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_approve_leave(params: LeaveIdInput) -> str:
    """Approve a leave request. Requires Admin/Owner role."""
    try:
        data = await api_request("POST", f"/leaves/{params.leave_id}/approve")
        return f"Approved leave {params.leave_id}."
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_deny_leave",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
)
async def early_deny_leave(params: LeaveIdInput) -> str:
    """Deny a leave request. Requires Admin/Owner role."""
    try:
        await api_request("POST", f"/leaves/{params.leave_id}/deny")
        return f"Denied leave {params.leave_id}."
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_delete_leave",
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
)
async def early_delete_leave(params: LeaveIdInput) -> str:
    """Delete a leave. Irreversible. Requires Admin/Owner for other users' leaves."""
    try:
        await api_request("DELETE", f"/leaves/{params.leave_id}")
        return f"Deleted leave {params.leave_id}."
    except Exception as e:
        return handle_error(e)


# ============ Webhook Tools ============

@mcp.tool(
    name="early_list_webhook_events",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_list_webhook_events(params: EmptyInput) -> str:
    """List available webhook events."""
    try:
        data = await api_request("GET", "/webhooks/event")
        events = data.get("events", [])
        lines = ["## Available Webhook Events"]
        for e in events:
            lines.append(f"- {e}")
        return "\n".join(lines)
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_list_webhook_subscriptions",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_list_webhook_subscriptions(params: EmptyInput) -> str:
    """List all webhook subscriptions."""
    try:
        data = await api_request("GET", "/webhooks/subscription")
        subs = data.get("subscriptions", [])
        if not subs:
            return "No webhook subscriptions."
        
        lines = ["## Webhook Subscriptions"]
        for s in subs:
            lines.append(f"- **{s['event']}** → {s['target_url']} (ID: {s['id']})")
        return "\n".join(lines)
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_subscribe_webhook",
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
)
async def early_subscribe_webhook(params: WebhookSubscribeInput) -> str:
    """Subscribe to a webhook event. URL must be HTTPS and publicly reachable."""
    try:
        data = await api_request("POST", "/webhooks/subscription", {
            "event": params.event,
            "target_url": params.target_url
        })
        return f"Subscribed to {params.event}. Subscription ID: {data.get('id', '?')}"
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_unsubscribe_webhook",
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
)
async def early_unsubscribe_webhook(params: WebhookIdInput) -> str:
    """Unsubscribe from a webhook."""
    try:
        await api_request("DELETE", f"/webhooks/subscription/{params.subscription_id}")
        return f"Unsubscribed webhook {params.subscription_id}."
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_unsubscribe_all_webhooks",
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
)
async def early_unsubscribe_all_webhooks(params: EmptyInput) -> str:
    """Unsubscribe from all webhooks."""
    try:
        await api_request("DELETE", "/webhooks/subscription")
        return "Unsubscribed from all webhooks."
    except Exception as e:
        return handle_error(e)


# ============ Report Tools ============

@mcp.tool(
    name="early_generate_report",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_generate_report(params: ReportInput) -> str:
    """Generate a time tracking report with aggregated data.

    Breaks down totals by activity, and by user when entries from multiple
    team members are present. Omit user_ids to include every entry you have
    Full access to across folders; pass user_ids to scope to specific members.
    Seeing other members' entries requires Full access to their folder.
    """
    try:
        body = {
            "date": {"start": params.start_date, "end": params.end_date},
            "fileType": "json"
        }
        if params.activity_ids:
            body["activities"] = {"ids": params.activity_ids}
        if params.folder_ids:
            body["folders"] = {"ids": params.folder_ids}
        if params.user_ids:
            body["users"] = {"ids": params.user_ids}
        
        data = await api_request("POST", "/report", body)
        entries = data.get("timeEntries", [])
        
        if not entries:
            return f"No entries in report for {params.start_date} to {params.end_date}."
        
        by_activity = {}
        by_user = {}
        total_seconds = 0
        
        for e in entries:
            activity_name = e.get("activity", {}).get("name", "Unknown")
            user = e.get("user") or {}
            user_label = user.get("name") or user.get("email") or "Unknown"
            duration = e.get("duration", {})
            try:
                s = datetime.fromisoformat(duration["startedAt"].split(".")[0])
                t = datetime.fromisoformat(duration["stoppedAt"].split(".")[0])
                secs = int((t - s).total_seconds())
                by_activity[activity_name] = by_activity.get(activity_name, 0) + secs
                by_user[user_label] = by_user.get(user_label, 0) + secs
                total_seconds += secs
            except:
                pass
        
        lines = [f"## Report: {params.start_date} to {params.end_date}", ""]
        
        if len(by_user) > 1:
            lines.append("### By User")
            for name, secs in sorted(by_user.items(), key=lambda x: -x[1]):
                h, rem = divmod(secs, 3600)
                m = rem // 60
                pct = (secs / total_seconds * 100) if total_seconds else 0
                lines.append(f"- **{name}**: {h}h {m}m ({pct:.1f}%)")
            lines.append("")
        
        lines.append("### By Activity")
        for name, secs in sorted(by_activity.items(), key=lambda x: -x[1]):
            h, rem = divmod(secs, 3600)
            m = rem // 60
            pct = (secs / total_seconds * 100) if total_seconds else 0
            lines.append(f"- **{name}**: {h}h {m}m ({pct:.1f}%)")
        
        total_h, total_rem = divmod(total_seconds, 3600)
        total_m = total_rem // 60
        user_note = f", {len(by_user)} users" if len(by_user) > 1 else ""
        lines.append(f"\n**Total: {total_h}h {total_m}m** ({len(entries)} entries{user_note})")
        
        return "\n".join(lines)
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_analyze_time_distribution",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_analyze_time_distribution(params: ReportInput) -> str:
    """Return a structured per-user x per-activity time breakdown for anomaly analysis.

    This tool intentionally applies NO fixed thresholds. It returns the raw
    distribution (hours and each user's share of their own time per activity)
    plus team baselines so the calling LLM can reason about odd patterns, e.g.
    a member booking unusually high time on a given activity vs the team.
    Omit user_ids to include every entry you have Full access to; pass user_ids
    to scope to specific members. Seeing other members' entries requires Full
    access to their folder.
    """
    try:
        body = {
            "date": {"start": params.start_date, "end": params.end_date},
            "fileType": "json"
        }
        if params.activity_ids:
            body["activities"] = {"ids": params.activity_ids}
        if params.folder_ids:
            body["folders"] = {"ids": params.folder_ids}
        if params.user_ids:
            body["users"] = {"ids": params.user_ids}

        data = await api_request("POST", "/report", body)
        entries = data.get("timeEntries", [])

        if not entries:
            return f"No entries in report for {params.start_date} to {params.end_date}."

        matrix = {}
        user_totals = {}
        activity_totals = {}

        for e in entries:
            user = e.get("user") or {}
            user_label = user.get("name") or user.get("email") or "Unknown"
            activity_name = e.get("activity", {}).get("name", "Unknown")
            duration = e.get("duration", {})
            try:
                s = datetime.fromisoformat(duration["startedAt"].split(".")[0])
                t = datetime.fromisoformat(duration["stoppedAt"].split(".")[0])
                secs = int((t - s).total_seconds())
            except:
                continue
            matrix.setdefault(user_label, {})
            matrix[user_label][activity_name] = matrix[user_label].get(activity_name, 0) + secs
            user_totals[user_label] = user_totals.get(user_label, 0) + secs
            activity_totals[activity_name] = activity_totals.get(activity_name, 0) + secs

        users = sorted(matrix)
        activities = sorted(activity_totals, key=lambda a: -activity_totals[a])
        grand_total = sum(user_totals.values())

        def hours(secs):
            return secs / 3600

        lines = [f"## Time Distribution: {params.start_date} to {params.end_date}", ""]
        lines.append(
            f"{len(entries)} entries, {len(users)} users, {len(activities)} activities, "
            f"{hours(grand_total):.1f}h total"
        )
        lines.append("")

        lines.append("### Per-user x activity (hours, share of user's own time)")
        header = "| User | " + " | ".join(activities) + " | Total |"
        separator = "|" + "---|" * (len(activities) + 2)
        lines.append(header)
        lines.append(separator)
        for u in users:
            user_total = user_totals[u]
            cells = []
            for a in activities:
                secs = matrix[u].get(a, 0)
                if secs and user_total:
                    cells.append(f"{hours(secs):.1f}h ({secs / user_total * 100:.0f}%)")
                else:
                    cells.append("-")
            lines.append(f"| {u} | " + " | ".join(cells) + f" | {hours(user_total):.1f}h |")
        lines.append("")

        lines.append("### Team baseline per activity")
        for a in activities:
            shares = [matrix[u].get(a, 0) / user_totals[u] for u in users if user_totals[u] > 0]
            avg_share = (sum(shares) / len(shares) * 100) if shares else 0
            avg_hours = hours(activity_totals[a]) / len(users) if users else 0
            pct_grand = (activity_totals[a] / grand_total * 100) if grand_total else 0
            lines.append(
                f"- **{a}**: {hours(activity_totals[a]):.1f}h total, "
                f"avg {avg_hours:.1f}h/user, avg {avg_share:.0f}% of own time, "
                f"{pct_grand:.0f}% of grand total"
            )

        return "\n".join(lines)
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_export_raw_entries_for_range",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_export_raw_entries_for_range(params: ReportInput) -> str:
    """Export RAW individual time entries for a date range, grouped by user.

    Unlike early_generate_report / early_analyze_time_distribution (which
    aggregate), this returns every entry's date, start, stop, duration, activity,
    note, and entry ID so an LLM can spot fine-grained patterns (time-of-day,
    weekend work, suspicious durations, note content). Entries are grouped per
    user and sorted chronologically. Timestamps are UTC (no offset); each entry
    includes its tracking timezone, so convert UTC to that zone before reasoning
    about time-of-day or weekday/weekend. Each user's header summarizes their
    tracking timezone(s) - a hint about location - and flags users tracking across
    multiple timezones (possible travel/relocation).

    Omit user_ids to include every member you have Full folder access to; pass
    user_ids to scope to specific members. Seeing other members' entries requires
    Full access to their folder. Large date ranges or teams can produce long
    output; narrow the range or filter to keep responses manageable.
    """
    try:
        body = {
            "date": {"start": params.start_date, "end": params.end_date},
            "fileType": "json"
        }
        if params.activity_ids:
            body["activities"] = {"ids": params.activity_ids}
        if params.folder_ids:
            body["folders"] = {"ids": params.folder_ids}
        if params.user_ids:
            body["users"] = {"ids": params.user_ids}

        data = await api_request("POST", "/report", body)
        entries = data.get("timeEntries", [])

        if not entries:
            return f"No entries in report for {params.start_date} to {params.end_date}."

        by_user = {}
        for e in entries:
            user = e.get("user") or {}
            label = user.get("name") or user.get("email") or "Unknown"
            by_user.setdefault(label, []).append(e)

        lines = [
            f"## Team Time Entries Export: {params.start_date} to {params.end_date}",
            "",
            f"{len(entries)} entries across {len(by_user)} users",
            "",
            "_Timestamps are UTC. Each entry shows its tracking timezone (tz=...); "
            "convert UTC to that zone before reasoning about time-of-day or weekday/weekend._",
            "",
        ]

        for label in sorted(by_user):
            user_entries = by_user[label]
            user_entries.sort(key=lambda e: e.get("duration", {}).get("startedAt", ""))

            total_seconds = 0
            tz_counts = {}
            rendered = []
            for e in user_entries:
                duration = e.get("duration", {})
                started = duration.get("startedAt", "")
                stopped = duration.get("stoppedAt", "")
                activity = e.get("activity", {}).get("name", "?")
                tz = e.get("timezone") or "?"
                tz_counts[tz] = tz_counts.get(tz, 0) + 1
                note = e.get("note") or {}
                note_text = note.get("text", "") if note else ""

                dur_str = format_duration(started, stopped)
                try:
                    s = datetime.fromisoformat(started.split(".")[0])
                    t = datetime.fromisoformat(stopped.split(".")[0])
                    total_seconds += int((t - s).total_seconds())
                except:
                    pass

                line = (
                    f"- {started[:10]} {started[11:16]}\u2192{stopped[11:16]} UTC "
                    f"({dur_str}) **{activity}** [id: {e.get('id', '?')}, tz={tz}]"
                )
                if note_text:
                    line += f" \u2014 {note_text[:120]}"
                rendered.append(line)

            total_h, rem = divmod(total_seconds, 3600)
            total_m = rem // 60
            user = (user_entries[0].get("user") or {})
            email = user.get("email", "")
            email_part = f" ({email})" if email else ""
            tz_summary = ", ".join(
                f"{z} ({c})" for z, c in sorted(tz_counts.items(), key=lambda x: -x[1])
            )
            tz_flag = " ⚠ multiple timezones" if len(tz_counts) > 1 else ""
            lines.append(f"### {label}{email_part} \u2014 {len(user_entries)} entries, {total_h}h {total_m}m")
            lines.append(f"_timezones: {tz_summary}{tz_flag}_")
            lines.extend(rendered)
            lines.append("")

        return "\n".join(lines)
    except Exception as e:
        return handle_error(e)


@mcp.tool(
    name="early_today_summary",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
)
async def early_today_summary(params: EmptyInput) -> str:
    """Get a summary of today's tracked time."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        start = f"{today}T00:00:00.000"
        end = f"{today}T23:59:59.999"
        
        data = await api_request("GET", f"/time-entries/{start}/{end}")
        entries = data.get("timeEntries", [])
        
        # Check current tracking (handle 404 gracefully)
        tracking = None
        try:
            tracking = await api_request("GET", "/tracking")
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise
        
        by_activity = {}
        total_seconds = 0
        
        for e in entries:
            activity_name = e.get("activity", {}).get("name", "Unknown")
            duration = e.get("duration", {})
            try:
                s = datetime.fromisoformat(duration["startedAt"].split(".")[0])
                t = datetime.fromisoformat(duration["stoppedAt"].split(".")[0])
                secs = int((t - s).total_seconds())
                by_activity[activity_name] = by_activity.get(activity_name, 0) + secs
                total_seconds += secs
            except:
                pass
        
        lines = [f"## Today's Summary ({today})", ""]
        
        # Current tracking
        if tracking and tracking.get("activity"):
            activity = tracking.get("activity", {})
            started = tracking.get("startedAt", "")
            try:
                start_dt = datetime.fromisoformat(started.split(".")[0])
                elapsed = int((datetime.now() - start_dt).total_seconds())
                h, rem = divmod(elapsed, 3600)
                m = rem // 60
                lines.append(f"🔴 **Currently tracking:** {activity.get('name', '?')} ({h}h {m}m)")
                lines.append("")
            except:
                lines.append(f"🔴 **Currently tracking:** {activity.get('name', '?')}")
                lines.append("")
        
        if by_activity:
            lines.append("### Completed")
            for name, secs in sorted(by_activity.items(), key=lambda x: -x[1]):
                h, rem = divmod(secs, 3600)
                m = rem // 60
                lines.append(f"- {name}: {h}h {m}m")
            
            total_h, total_rem = divmod(total_seconds, 3600)
            total_m = total_rem // 60
            lines.append(f"\n**Total completed: {total_h}h {total_m}m**")
        else:
            lines.append("No completed time entries today.")
        
        return "\n".join(lines)
    except Exception as e:
        return handle_error(e)


if __name__ == "__main__":
    mcp.run()
