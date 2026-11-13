# KanMind Backend

REST API for **KanMind**, a kanban board application. Built with Django and
Django REST Framework. This repository contains the backend only; the
frontend (Vanilla JS) is provided separately by the Developer Akademie.

## Tech stack

- Python 3.12+
- Django 6.1
- Django REST Framework (token authentication)
- django-cors-headers
- SQLite (development database)

## Getting started

```bash
# 1. Clone the repository
git clone <your-repository-url>
cd KanMind-backend

# 2. Create and activate a virtual environment
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the database
python manage.py migrate

# 5. (Optional) create an admin user for /admin/
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`, which is the
`API_BASE_URL` the frontend expects.

### Connecting the frontend

1. Start the backend as described above.
2. Open the frontend project in VS Code and start `index.html` with
   **Live Server**.
3. CORS is open for all origins in development, so no further setup is
   needed.

### Guest login

The frontend's "Guest Log in" button uses `kevin@kovacsi.de` /
`asdasdasd`. This user is not created automatically. Register it once,
e.g. via the frontend sign-up page or:

```bash
curl -X POST http://127.0.0.1:8000/api/registration/ \
  -H "Content-Type: application/json" \
  -d '{"fullname": "Kevin Kovacs", "email": "kevin@kovacsi.de", "password": "asdasdasd", "repeated_password": "asdasdasd"}'
```

## Project structure

```
core/         Project settings and root URLs
auth_app/     Custom user model (login with email), registration, login, email check
boards_app/   Board model and board endpoints
tasks_app/    Task and comment models and endpoints
```

Each app keeps its API code in an `api/` package (`serializers.py`,
`views.py`, `urls.py`, `permissions.py`).

## Authentication

Token authentication. Registration and login return a token; send it with
every other request:

```
Authorization: Token <your-token>
```

All endpoints except registration and login require authentication
(otherwise `401`).

## API endpoints

| Method | Endpoint                                     | Description |
|--------|----------------------------------------------|-------------|
| POST   | `/api/registration/`                         | Register (`fullname`, `email`, `password`, `repeated_password`) |
| POST   | `/api/login/`                                | Log in (`email`, `password`) |
| GET    | `/api/email-check/?email=<email>`            | Look up a user by email (404 if not found) |
| GET    | `/api/boards/`                               | Boards the user owns or is a member of |
| POST   | `/api/boards/`                               | Create a board (`title`, `members` = list of user ids) |
| GET    | `/api/boards/{id}/`                          | Board with members and tasks |
| PATCH  | `/api/boards/{id}/`                          | Update `title` and/or `members` |
| DELETE | `/api/boards/{id}/`                          | Delete a board (owner only) |
| GET    | `/api/tasks/assigned-to-me/`                 | Tasks assigned to the user |
| GET    | `/api/tasks/reviewing/`                      | Tasks the user reviews |
| POST   | `/api/tasks/`                                | Create a task |
| PATCH  | `/api/tasks/{id}/`                           | Update a task |
| DELETE | `/api/tasks/{id}/`                           | Delete a task (creator or board owner) |
| GET    | `/api/tasks/{task_id}/comments/`             | List comments of a task |
| POST   | `/api/tasks/{task_id}/comments/`             | Add a comment (`content`) |
| DELETE | `/api/tasks/{task_id}/comments/{comment_id}/`| Delete a comment (author only) |

Task values:

- `status`: `to-do`, `in-progress`, `review`, `done`
- `priority`: `low`, `medium`, `high`

### Special behaviour

- The board owner is always a member of the board; it is added
  automatically on create and cannot be removed via PATCH.
- `GET/PATCH/DELETE /api/boards/{id}` also works **without** a trailing
  slash, because the frontend calls it that way (a redirect would break
  the CORS preflight).
- Only board members (incl. owner) can read a board, create/update tasks
  on it and read/write its comments (`403` otherwise, `404` if the object
  does not exist).
- `assignee_id` and `reviewer_id` must be members of the task's board and
  may be `null`.
- The board of a task cannot be changed via PATCH.
- `PUT` is not supported; use `PATCH`.

## Running the tests

```bash
python manage.py test
```

With coverage (install the tool first with `pip install coverage`):

```bash
coverage run manage.py test
coverage report
```

## Notes

- `DEBUG = True` and the secret key in `core/settings.py` are meant for
  local development only. Change both before any public deployment.
- The SQLite database (`db.sqlite3`) is excluded via `.gitignore` and must
  never be committed.
- The frontend is not part of this repository.
