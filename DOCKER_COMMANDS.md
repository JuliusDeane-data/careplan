# Docker Commands Cheat Sheet

## Server Management

### Check if containers are running
```bash
docker compose ps
```

### Start all containers
```bash
docker compose up -d
```

### Stop all containers
```bash
docker compose down
```

### Restart containers
```bash
docker compose restart
```

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f db
docker compose logs -f celery
```

## Django Management Commands

### Run any Django command
```bash
docker compose exec web python manage.py <command>
```

### Common commands:
```bash
# Make migrations
docker compose exec web python manage.py makemigrations

# Apply migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Django shell
docker compose exec web python manage.py shell

# Run tests
docker compose exec web python manage.py test

# Collect static files
docker compose exec web python manage.py collectstatic

# Check for issues
docker compose exec web python manage.py check
```

## Database Commands

### Access PostgreSQL shell
```bash
docker compose exec db psql -U postgres -d careplan
```

### Database backup
```bash
docker compose exec db pg_dump -U postgres careplan > backup.sql
```

### Database restore
```bash
docker compose exec -T db psql -U postgres careplan < backup.sql
```

## Redis Commands

### Access Redis CLI
```bash
docker compose exec redis redis-cli
```

### Clear Redis cache
```bash
docker compose exec redis redis-cli FLUSHALL
```

## Debugging

### Access container shell
```bash
docker compose exec web bash
docker compose exec db sh
```

### View container resource usage
```bash
docker stats
```

### Rebuild containers (after Dockerfile changes)
```bash
docker compose build
docker compose up -d
```

### Remove everything and start fresh
```bash
docker compose down -v  # -v removes volumes too
docker compose up -d --build
```

## Accessing the Application

- **Web**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **Database**: localhost:5433 (PostgreSQL)
- **Redis**: localhost:6380

## Login Credentials

- **Username**: admin
- **Password**: admin123

## Notes

⚠️ **Do NOT run `python manage.py` directly** - Django is only installed in Docker
✅ **Always use** `docker compose exec web python manage.py <command>`
📝 The server auto-reloads when you change code (volume mounted)
🗄️ Database data persists in Docker volumes even after `docker compose down`
