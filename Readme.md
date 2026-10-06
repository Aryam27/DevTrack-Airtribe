# DevTrack — Engineering Issue Tracker API

A small Django backend for tracking engineering issues, similar to a stripped-down GitHub Issues. Reporters file issues, issues have a status and a priority, and everything is stored in two JSON files. Built with plain Django (`JsonResponse`) and a Python OOP model layer.

## How to run

```bash
# 1. Create and activate a virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install django

# 3. Start the server
python manage.py runserver
```

The API is now available at `http://localhost:8000/api/`.

Data is stored in `reporters.json` and `issues.json` in the project root. Both files must exist and contain `[]` on a fresh start.

## Project structure

```
devtrack/
├── manage.py
├── reporters.json        # reporter data
├── issues.json           # issue data
├── screenshots/
│   ├── Reporter_API_SS/  # Postman screenshots for /api/reporters/
│   └── Issues_api_SS/    # Postman screenshots for /api/issues/
├── devtrack/             # project config (settings.py, urls.py)
└── issues/
    ├── models.py         # OOP classes: BaseEntity, Reporter, Issue, CriticalIssue, LowPriorityIssue
    ├── views.py          # endpoint logic and JSON file helpers
    └── urls.py           # app routes
```

## Data model

**Reporter:** `id` (int), `name`, `email`, `team`

**Issue:** `id` (int), `title`, `description`, `status`, `priority`, `reporter_id`, `created_at`

- `status` is one of: `open`, `in_progress`, `resolved`, `closed`
- `priority` is one of: `low`, `medium`, `high`, `critical`
- One reporter can file many issues. `reporter_id` is stored inside the issue.

## OOP design

```
BaseEntity (abstract: validate(), to_dict())
├── Reporter
└── Issue                  describe() -> "{title} [{priority}]"
    ├── CriticalIssue      describe() -> "[URGENT] {title} — needs immediate attention"
    └── LowPriorityIssue   describe() -> "{title} — low priority, handle when free"
```

- `BaseEntity` is abstract, so every entity must implement its own `validate()`. `to_dict()` is written once and inherited.
- `POST /api/issues/` creates a `CriticalIssue` for priority `critical`, a `LowPriorityIssue` for `low`, and a plain `Issue` for `medium` and `high`. The response includes `describe()` as `message`.

## Endpoints

### Reporters

| Method | URL | What it does |
|---|---|---|
| POST | `/api/reporters/` | Create a reporter |
| GET | `/api/reporters/` | Get all reporters |
| GET | `/api/reporters/?id=1` | Get one reporter by id |

### Issues

| Method | URL | What it does |
|---|---|---|
| POST | `/api/issues/` | Create an issue (reporter must exist) |
| GET | `/api/issues/` | Get all issues |
| GET | `/api/issues/?id=1` | Get one issue by id |
| GET | `/api/issues/?status=open` | Get all issues with the given status |

### Status codes

| Code | When |
|---|---|
| 200 | Successful GET |
| 201 | Successful POST |
| 400 | Validation failure, invalid JSON, non-numeric id, duplicate issue id, or unknown `reporter_id` |
| 404 | Record not found by id |
| 405 | HTTP method not supported on that URL |

### Example: create an issue

`POST /api/issues/`

```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1
}
```

Response `201 Created`:

```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1,
  "created_at": "2026-10-06 17:12:12.965902",
  "message": "[URGENT] Login button not working on mobile — needs immediate attention"
}
```

Error response `400 Bad Request`:

```json
{ "error": "Title cannot be empty" }
```

Error response `404 Not Found`:

```json
{ "error": "Issue not found" }
```

## Postman screenshots

Screenshots are split into two folders: `screenshots/Reporter_API_SS/` and `screenshots/Issues_api_SS/`.

### Success: create an issue (201)

![POST issue success](<screenshots/Issues_api_SS/POST_api_issues_Pass.png>)

### Failure: empty title (400)

![POST issue failure](<screenshots/Issues_api_SS/POST bad data is wrongly accepted (FIXED).png>)

### Failure: issue not found (404)

![GET issue 404](<screenshots/Issues_api_SS/GET_api_invalid_id_base_Error_fixed.png>)

### Other successful requests

| Request | Screenshot |
|---|---|
| `POST /api/reporters/` (valid reporter) | ![](<screenshots/Reporter_API_SS/POST bad data is wrongly accepted (FIXED).png>) |
| `GET /api/issues/` | ![](<screenshots/Issues_api_SS/GET_API_Error_fixed.png>) |
| `GET /api/issues/?id=1` | ![](<screenshots/Issues_api_SS/GET_api_id_base_Error_fixed.png>) |
| `GET /api/issues/?status=open` | ![](<screenshots/Issues_api_SS/GET_status_Error_Fixed.png>) |
| `GET /api/reporters/` | ![](<screenshots/Reporter_API_SS/GET_API_Error_Fixed.png>) |
| `GET /api/reporters/?id=1` | ![](<screenshots/Reporter_API_SS/GET_API_ID_based_Error_Fixed.png>) |
| `GET /api/reporters/?id=99` (404) | ![](<screenshots/Reporter_API_SS/GET_FIXED_unknown_id.png>) |

## Development log: red, then green

Each feature was built in two steps. I first sent the request against code that did not yet handle it and captured the failure (red). I then wrote the fix and sent the same request again (green).

| Round | Request | Red (before) | Green (after) |
|---|---|---|---|
| 1 | POST reporter | ![](<screenshots/Reporter_API_SS/POST_api_reporters_fail.png>) 403, CSRF blocks the request | ![](<screenshots/Reporter_API_SS/POST_api_reporters_Pass.png>) 201 |
| 2 | POST reporter with bad data | ![](<screenshots/Reporter_API_SS/POST bad data is wrongly accepted.png>) 201, bad data accepted | ![](<screenshots/Reporter_API_SS/POST bad data is wrongly accepted (FIXED.).png>) 400 |
| 3 | GET reporters | ![](<screenshots/Reporter_API_SS/GET_API_Error.png>) 405 | ![](<screenshots/Reporter_API_SS/GET_API_Error_Fixed.png>) 200 |
| 4 | GET reporter by id | ![](<screenshots/Reporter_API_SS/GET_API_ID_based_Error.png>) 405 | ![](<screenshots/Reporter_API_SS/GET_API_ID_based_Error_Fixed.png>) 200 |
| 5 | POST issue | ![](<screenshots/Issues_api_SS/POST_api_issues_Fails.png>) 404, route missing | ![](<screenshots/Issues_api_SS/POST_api_issues_Pass.png>) 201 |
| 6 | POST issue with empty title | ![](<screenshots/Issues_api_SS/POST bad data is wrongly accepted.png>) 201, bad data accepted | ![](<screenshots/Issues_api_SS/POST bad data is wrongly accepted (FIXED).png>) 400 |
| 7 | GET issues | ![](<screenshots/Issues_api_SS/GET_API_Error.png>) 405 | ![](<screenshots/Issues_api_SS/GET_API_Error_fixed.png>) 200 |
| 8 | GET issue by id | ![](<screenshots/Issues_api_SS/GET_API_ID_based _Error.png>) 405 | ![](<screenshots/Issues_api_SS/GET_api_id_base_Error_fixed.png>) 200 |
| 9 | GET issues by status | ![](<screenshots/Issues_api_SS/GET_status_Error_.png>) 405 | ![](<screenshots/Issues_api_SS/GET_status_Error_Fixed.png>) 200 |
| 10 | POST issue with unknown reporter | ![](<screenshots/Issues_api_SS/Post issue reporter must exist_error.png>) 201, orphan issue saved | ![](<screenshots/Issues_api_SS/Post issue reporter must exist_fixed.png>) 400 |

## Design decision

**Validation lives inside the model classes, not in the views.**

Each entity owns its own rules through `validate()`. `Issue.validate()` checks the id, title, status and priority, and `Reporter.validate()` checks the id, name, email and team. The views only build the object, call `validate()`, and turn a `ValueError` into a `400` response.

Why: the rules sit in one place, so changing a rule never means hunting through view code. Every subclass (`CriticalIssue`, `LowPriorityIssue`) inherits the same validation for free, and the views stay short enough to read at a glance.

Trade-off: `validate()` stops at the first error, so a request with several mistakes reports them one at a time. Collecting all errors into a list would be friendlier, at the cost of more code.

## Notes and limitations

- JSON files are fine for this exercise but not for production. Concurrent writes can corrupt them, and every request reads the whole file.
- `@csrf_exempt` is used on the views because this API has no login or cookies, so there is no session for a forged request to abuse.
- Ids are supplied by the client, as in the brief. Duplicate issue ids are rejected with `400`. Reporter ids are not checked for duplicates yet.