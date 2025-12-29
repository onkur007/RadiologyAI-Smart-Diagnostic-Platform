# Docker Deployment Guide

This guide explains how to run the application using Docker.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed
- Gemini API key

## Quick Start with Docker

### 1. Create `.env` file

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your-gemini-api-key-here
SECRET_KEY=your-secret-key-here
```

### 2. Run with Docker Compose

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Build and run the FastAPI application
- Expose API on http://localhost:8000

### 3. Initialize Database

```bash
# Access the app container
docker exec -it radiology_app bash

# Run initialization script
python init_db.py

# Exit container
exit
```

### 4. Access the Application

- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

### Access database
```bash
docker exec -it radiology_db psql -U radiology_user -d radiology_ai
```

### Clean up everything
```bash
docker-compose down -v
```

## Production Deployment

### Using Docker

1. **Build image**:
```bash
docker build -t radiology-ai:latest .
```

2. **Run container**:
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="your-database-url" \
  -e SECRET_KEY="your-secret-key" \
  -e GEMINI_API_KEY="your-api-key" \
  -v $(pwd)/uploads:/app/uploads \
  --name radiology-ai \
  radiology-ai:latest
```

### Environment Variables

Required:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `GEMINI_API_KEY`: Google Gemini API key

Optional:
- `DEBUG`: Set to `False` in production
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `MAX_UPLOAD_SIZE`: Maximum file upload size

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs app

# Check if ports are available
netstat -ano | findstr :8000
```

### Database connection fails
```bash
# Check if database is healthy
docker-compose ps

# Restart services
docker-compose restart
```

### Out of disk space
```bash
# Remove unused images
docker system prune

# Remove all stopped containers
docker container prune
```

## Notes

- Database data persists in Docker volume `postgres_data`
- Uploaded files are mounted to `./uploads` directory
- Application auto-reloads on code changes in development mode
