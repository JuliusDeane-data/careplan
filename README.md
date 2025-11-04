# Careplan - Care Worker Management System

A modular management software for care workers, designed to handle employee management, shift planning, vacation tracking, and more.

## Features

- **Employee Management**: Comprehensive employee profiles with qualifications, locations, and HR data
- **Vacation Planning**: Interactive calendar-based vacation request and approval system
- **Location Management**: Multi-location support with employee assignments
- **Notifications**: Real-time notifications for approvals, updates, and system events
- **Scalable Architecture**: Built to support 100+ concurrent users

## Technology Stack

- **Backend**: Django 5.2.7 with Django REST Framework
- **Database**: PostgreSQL 15+
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Containerization**: Docker & Docker Compose

## Project Structure

```
careplan/
├── apps/                   # Django applications
│   ├── core/              # Shared utilities and base models
│   ├── accounts/          # Authentication and user management
│   ├── employees/         # Employee profiles and HR data
│   ├── locations/         # Location management
│   ├── notifications/     # Notification system
│   └── vacation/          # Vacation planning module
├── config/                # Project configuration
│   ├── settings/          # Environment-specific settings
│   └── celery.py          # Celery configuration
├── requirements/          # Dependency files
├── tests/                 # Test files
└── docker-compose.yml     # Docker services configuration
```

## Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (recommended)
- PostgreSQL 15+ (if not using Docker)
- Redis (if not using Docker)

### Installation

#### Option 1: Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd careplan
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services**:
   ```bash
   docker-compose up --build
   ```

4. **Run migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access the application**:
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin

#### Option 2: Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd careplan
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Set up PostgreSQL and Redis** (install locally or use Docker for these services only):
   ```bash
   # Start only database and redis
   docker-compose up db redis -d
   ```

5. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**:
   ```bash
   python manage.py runserver
   ```

9. **Run Celery worker** (in another terminal):
   ```bash
   celery -A config worker -l info
   ```

### Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `DJANGO_ENV`: Environment (development/production)
- `SECRET_KEY`: Django secret key
- `DB_*`: Database configuration
- `REDIS_URL`: Redis connection URL
- `EMAIL_*`: Email server configuration

## Development

### Running Tests

```bash
# Using Docker
docker-compose exec web pytest

# Local
pytest

# With coverage
pytest --cov=apps --cov-report=html
```

### Code Quality

```bash
# Format code with black
black .

# Sort imports
isort .

# Lint with flake8
flake8

# Run pylint
pylint apps/
```

### Creating a New App

```bash
# Create new Django app in apps directory
python manage.py startapp <app_name> apps/<app_name>

# Add to INSTALLED_APPS in config/settings/base.py
LOCAL_APPS = [
    ...
    'apps.<app_name>',
]
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations
```

## API Documentation

### Authentication

The API uses JWT authentication. To obtain a token:

```bash
POST /api/v1/auth/login/
{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "access": "access_token_here",
    "refresh": "refresh_token_here"
}
```

Use the access token in requests:
```bash
Authorization: Bearer <access_token>
```

### API Endpoints

Base URL: `http://localhost:8000/api/v1/`

- **Authentication**: `/auth/`
  - `POST /auth/login/` - Login
  - `POST /auth/logout/` - Logout
  - `POST /auth/refresh/` - Refresh token
  - `POST /auth/password/change/` - Change password

- **Employees**: `/employees/`
  - `GET /employees/` - List employees
  - `POST /employees/` - Create employee
  - `GET /employees/{id}/` - Employee details
  - `PUT/PATCH /employees/{id}/` - Update employee
  - `GET /employees/me/` - Current user's profile

- **Locations**: `/locations/`
  - `GET /locations/` - List locations
  - `POST /locations/` - Create location
  - `GET /locations/{id}/` - Location details

- **Vacation**: `/vacation/`
  - `GET /vacation/requests/` - List vacation requests
  - `POST /vacation/requests/` - Submit request
  - `GET /vacation/calendar/` - Calendar view
  - `POST /vacation/requests/{id}/approve/` - Approve request

## Deployment

### Production Checklist

1. Set `DJANGO_ENV=production` in environment
2. Use a strong `SECRET_KEY`
3. Set `DEBUG=False`
4. Configure `ALLOWED_HOSTS`
5. Set up proper database (PostgreSQL)
6. Configure Redis for caching and sessions
7. Set up email server (SMTP)
8. Enable HTTPS
9. Configure static file serving (Nginx + WhiteNoise)
10. Set up monitoring and logging
11. Configure backups

### Docker Production Deployment

1. Build production image:
   ```bash
   docker build -t careplan:latest .
   ```

2. Use production requirements:
   ```bash
   pip install -r requirements/production.txt
   ```

3. Run with Gunicorn:
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
   ```

4. Set up Nginx as reverse proxy

## Performance & Scalability

The application is optimized for 100+ concurrent users:

- **Database connection pooling** (CONN_MAX_AGE=600)
- **Redis caching** for sessions and query results
- **Celery** for async task processing
- **Optimized queries** with select_related/prefetch_related
- **Pagination** on all list endpoints
- **Rate limiting** to prevent abuse

### Performance Targets

- API response time: < 200ms (95th percentile)
- Database queries: < 100ms (95th percentile)
- Support 100+ concurrent users
- 99.9% uptime

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Write tests
4. Ensure code quality (black, flake8, isort)
5. Create pull request

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.
