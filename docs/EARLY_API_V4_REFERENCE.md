# Early (Timeular) API v4 Reference

**Base URL:** `https://api.early.app`

## Authentication

All secured endpoints require: `Authorization: Bearer {token}`

### Sign In
```
POST /api/v4/developer/sign-in
Content-Type: application/json

{
  "apiKey": "YOUR_API_KEY",
  "apiSecret": "YOUR_API_SECRET"
}

Response: { "token": "1234abcdEFGH" }
```

### Other Auth Endpoints
- `GET /api/v4/developer/api-access` - Fetch API key
- `POST /api/v4/developer/api-access` - Generate new API key/secret pair
- `POST /api/v4/developer/logout` - Invalidate token

---

## User & Team

### Get Current User
```
GET /api/v4/me

Response:
{
  "id": "1",
  "name": "My name",
  "email": "my-name@example.com"
}
```

### List All Users
```
GET /api/v4/users

Response:
{
  "users": [
    { "id": "1", "name": "My name", "email": "my-name@example.com" },
    { "id": "2", "name": "My teammate", "email": "my-teammate@example.com" }
  ]
}
```

---

## Activities

### List All Activities
```
GET /api/v4/activities

Response:
{
  "activities": [
    { "id": "1", "name": "abc", "color": "#000000", "folderId": "1" }
  ],
  "inactiveActivities": [...],
  "archivedActivities": [...]
}
```

### Create Activity
```
POST /api/v4/activities
{
  "name": "sleeping",
  "color": "#a1c2c3",
  "folderId": "123456"
}
```

### Edit Activity
```
PATCH /api/v4/activities/{id}
{
  "name": "deeper sleeping",
  "color": "#f9e8d7"
}
```

### Archive/Unarchive Activity
```
DELETE /api/v4/activities/{id}        # Archive
POST /api/v4/activities/{id}/unarchive # Unarchive
```

---

## Tracking (Live Timer)

### Get Current Tracking
```
GET /api/v4/tracking

Response:
{
  "id": 1,
  "activity": {
    "id": "1217348",
    "name": "abc",
    "color": "#000000",
    "folderId": "1"
  },
  "startedAt": "2020-08-03T04:00:00.000",
  "note": {
    "text": "99 sheep <{{|t|1|}}><{{|m|2|}}>",
    "tags": [
      { "id": 1, "key": "uuid", "label": "some tag", "scope": "timeular", "folderId": "1" }
    ],
    "mentions": [
      { "id": 2, "key": "uuid", "label": "some-mention", "scope": "timeular", "folderId": "1" }
    ]
  }
}
```

### Start Tracking
```
POST /api/v4/tracking/{activityId}/start
{
  "startedAt": "2016-02-03T04:00:00.000"
}
```

### Stop Tracking (Creates Time Entry)
```
POST /api/v4/tracking/stop
{
  "stoppedAt": "2016-02-03T05:00:00.000"
}

Response: Returns the created time entry
```

### Edit Current Tracking
```
PATCH /api/v4/tracking
{
  "note": {
    "text": "99 sheep <{{|t|1|}}> <{{|m|1|}}>"
  },
  "activityId": "1",
  "startedAt": "2016-02-03T04:00:00.000"
}
```

### Cancel Tracking (No Time Entry Created)
```
DELETE /api/v4/tracking
```

---

## Time Entries

### List Time Entries in Range
```
GET /api/v4/time-entries/{startedAfter}/{startedBefore}

Example: GET /api/v4/time-entries/2024-01-01T00:00:00.000/2024-12-31T23:59:59.999

Response:
{
  "timeEntries": [
    {
      "id": "1",
      "activity": { "id": "1", "name": "abc", "color": "#000000", "folderId": "1" },
      "duration": {
        "startedAt": "2020-01-01T00:00:00.000",
        "stoppedAt": "2020-01-01T01:00:00.000"
      },
      "note": {
        "text": "Note with <{{|t|1|}}><{{|m|1|}}>",
        "tags": [...],
        "mentions": [...]
      }
    }
  ]
}
```

### Get Single Time Entry
```
GET /api/v4/time-entries/{id}
```

### Create Time Entry
```
POST /api/v4/time-entries
{
  "activityId": "1",
  "startedAt": "2016-08-05T06:00:00.000",
  "stoppedAt": "2016-08-05T07:00:00.000",
  "note": {
    "text": "99 sheep <{{|t|1|}}> <{{|m|1|}}>"
  }
}
```

**Note Format:** Tags use `<{{|t|ID|}}>`, mentions use `<{{|m|ID|}}>`

### Edit Time Entry
```
PATCH /api/v4/time-entries/{id}
{
  "activityId": "1",
  "startedAt": "2016-08-05T06:01:00.000",
  "stoppedAt": "2016-08-05T07:01:00.000",
  "note": {
    "text": "200 sheep <{{|t|1|}}> <{{|m|1|}}>"
  }
}
```

### Delete Time Entry
```
DELETE /api/v4/time-entries/{id}
```

---

## Reports

### Generate Report
```
POST /api/v4/report
{
  "date": {
    "start": "2017-02-01",
    "end": "2017-02-28"
  },
  "fileType": "json",  // or "csv", "xlsx" (pro only)
  "activities": {
    "ids": ["1"],
    "status": "active"  // or "archived"
  },
  "users": { "ids": ["1"] },
  "folders": { "ids": ["1"] },
  "tags": { "ids": [1] },
  "mentions": { "ids": [1] },
  "operator": "OR",  // or "AND"
  "noteQuery": "text"
}

Response (JSON):
{
  "timeEntries": [
    {
      "id": "1",
      "activity": {...},
      "user": { "id": "1", "name": "My name", "email": "..." },
      "folder": { "id": "1", "name": "My folder" },
      "duration": { "startedAt": "...", "stoppedAt": "..." },
      "note": {...},
      "timezone": "Europe/Berlin"
    }
  ]
}
```

---

## Tags & Mentions

### List All Tags & Mentions
```
GET /api/v4/tags-and-mentions

Response:
{
  "tags": [
    { "id": 1, "key": "1234", "label": "some-tag", "scope": "timeular", "folderId": "1" }
  ],
  "mentions": [
    { "id": 1, "key": "4321", "label": "some mention", "scope": "timeular", "folderId": "1" }
  ]
}
```

### Create Tag
```
POST /api/v4/tags
{
  "key": "tagtagtag",
  "label": "my new tag",
  "scope": "timeular",
  "folderId": "1"
}
```

### Update Tag
```
PATCH /api/v4/tags/{id}
{ "label": "New Label for tag" }
```

### Delete Tag
```
DELETE /api/v4/tags/{id}
```

### Create Mention
```
POST /api/v4/mentions
{
  "key": "mention",
  "label": "my new mention",
  "scope": "timeular",
  "folderId": "1"
}
```

### Update Mention
```
PATCH /api/v4/mentions/{id}
{ "label": "My new mention label" }
```

### Delete Mention
```
DELETE /api/v4/mentions/{id}
```

---

## Folders

### List All Folders
```
GET /api/v4/folders

Response:
{
  "folders": [
    {
      "id": "1",
      "name": "My folder",
      "status": "active",
      "members": [
        { "id": "1", "name": "My name", "email": "...", "accessLevel": "full" },
        { "id": "2", "name": "Teammate", "email": "...", "accessLevel": "personal" }
      ],
      "retiredMembers": [...]
    }
  ]
}
```

### Get Single Folder
```
GET /api/v4/folders/{id}
```

### Create Folder
```
POST /api/v4/folders
{
  "name": "My folder",
  "isWorkspaceFolder": true  // optional, defaults true
}
```

### Edit Folder
```
PATCH /api/v4/folders/{id}
{ "name": "Better name" }
```

### Archive/Unarchive Folder
```
POST /api/v4/folders/{id}/archive
POST /api/v4/folders/{id}/unarchive
```

### Delete Folder (IRREVERSIBLE)
```
DELETE /api/v4/folders/{id}
```

### Folder Members
```
GET /api/v4/folders/{folderId}/members
GET /api/v4/folders/{folderId}/members/{userId}
POST /api/v4/folders/{folderId}/members
  { "email": "teammate@example.com", "accessLevel": "personal" }
DELETE /api/v4/folders/{folderId}/members/{userId}
```

---

## Leaves (PTO)

### List Leaves
```
GET /api/v4/leaves?start=2025-01-01&end=2025-04-01
GET /api/v4/leaves?start=2025-01-01&end=2025-04-01&userId=1

Response:
{
  "timeLeaves": [
    {
      "id": "1",
      "typeId": "11",
      "startDate": "2025-02-17T00:00:00.000",
      "endDate": "2025-02-28T23:59:59.999",
      "note": null,
      "status": "approved",  // or "pending", "denied"
      "user": { "id": "1", "name": "My name", "email": "..." }
    }
  ]
}
```

### List Leave Types
```
GET /api/v4/leaves/types

Response:
{
  "types": [
    { "id": "1", "name": "Paid Leave" },
    { "id": "2", "name": "Sick Leave" },
    { "id": "3", "name": "Unpaid Leave" },
    { "id": "4", "name": "Public Holiday" },
    { "id": "5", "name": "Company Holiday" },
    { "id": "6", "name": "Sabbatical Leave" },
    { "id": "7", "name": "Bereavement Leave" },
    { "id": "8", "name": "Duvet Day" },
    { "id": "9", "name": "Gardening Leave" },
    { "id": "10", "name": "Time Off in Lieu" },
    { "id": "11", "name": "Carryover" },
    { "id": "12", "name": "Parental Leave" }
  ]
}
```

### Create Leave (for self)
```
POST /api/v4/leaves
{
  "typeId": "1",
  "startDate": "2025-01-01T06:00:00.000",
  "endDate": "2025-01-01T20:00:00.000",
  "note": "Time to relax"
}
```

### Create Leave for User (Admin only)
```
POST /api/v4/users/{userId}/leaves
{
  "typeId": "1",
  "startDate": "2025-01-01T06:00:00.000",
  "endDate": "2025-01-01T20:00:00.000",
  "note": "Extra day off"
}
```

### Approve/Deny Leave (Admin only)
```
POST /api/v4/leaves/{id}/approve
POST /api/v4/leaves/{id}/deny
```

### Delete Leave
```
DELETE /api/v4/leaves/{id}
```

---

## Webhooks

### Available Events
```
GET /api/v4/webhooks/event

Events:
- timeEntryCreated, timeEntryUpdated, timeEntryDeleted
- trackingStarted, trackingStopped, trackingEdited, trackingCanceled
- activityCreated, activityUpdated, activityDeleted
- folderCreated, folderUpdated, folderDeleted
- timeLeaveCreated, timeLeaveUpdated, timeLeaveDeleted, timeLeaveApproved, timeLeaveDenied
```

### List Subscriptions
```
GET /api/v4/webhooks/subscription

Response:
{
  "subscriptions": [
    { "id": "123456", "event": "trackingStarted", "target_url": "https://..." }
  ]
}
```

### Subscribe to Event
```
POST /api/v4/webhooks/subscription
{
  "event": "trackingStarted",
  "target_url": "https://example.org/some-endpoint"
}

Response: { "id": "123456" }
```

### Unsubscribe
```
DELETE /api/v4/webhooks/subscription/{id}
DELETE /api/v4/webhooks/subscription  # Unsubscribe all
```

---

## Date/Time Formats

- All timestamps: ISO 8601 format `YYYY-MM-DDTHH:mm:ss.SSS`
- Example: `2024-01-15T09:30:00.000`
- Report dates: `YYYY-MM-DD` format

## Error Responses

```json
{
  "message": "Explanation of what has happened"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
