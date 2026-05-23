# FarmFusion Backend Setup Guide

## Quick Start with Docker (Recommended)

1. Make sure you have Docker and Docker Compose installed

2. Build and start services:
```bash
docker-compose up --build
```

3. Access the API:
   - API Base URL: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

4. Run migrations:
```bash
docker-compose exec backend alembic upgrade head
```

## Local Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### 1. Environment Setup

Create virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Database Setup

Create PostgreSQL database:
```bash
createdb agri_db
```

Update `.env` file with your database credentials.

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start Services

Start Redis:
```bash
redis-server
```

Start Celery Worker:
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

Start API Server:
```bash
python run.py
# or
uvicorn app.main:app --reload --port 8000
```

## API Usage Examples

### Authentication

**Register:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "full_name": "John Farmer",
    "phone": "+91-9876543210",
    "password": "SecurePass123!"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=farmer@example.com&password=SecurePass123!"
```

**Get Profile:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Crops

**Get Crops:**
```bash
curl -X GET "http://localhost:8000/api/v1/crops" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Create Crop:**
```bash
curl -X POST "http://localhost:8000/api/v1/crops" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wheat",
    "variety": "HD-2967",
    "category": "cereals",
    "area_hectares": 2.5
  }'
```

**Get Recommendations:**
```bash
curl -X POST "http://localhost:8000/api/v1/crops/recommend" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "soil_type": "loamy",
    "ph_level": 7.0,
    "season": "rabi",
    "state": "Punjab"
  }'
```

### Mandi Prices

**Get Prices:**
```bash
curl -X GET "http://localhost:8000/api/v1/mandi/prices?commodity=wheat&state=Punjab" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Get Price Trend:**
```bash
curl -X GET "http://localhost:8000/api/v1/mandi/prices/trend/wheat?days=30" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing key | Required |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 |
| `WEATHER_API_KEY` | External weather API key | Optional |
| `MANDI_API_KEY` | Mandi prices API key | Optional |
| `SMS_API_KEY` | SMS provider API key | Optional |

## Production Deployment

1. Set secure values for all secrets in `.env`
2. Use PostgreSQL with SSL in production
3. Configure proper CORS origins
4. Set `DEBUG=false`
5. Use a process manager (systemd, supervisor)
6. Run behind Nginx reverse proxy
7. Enable HTTPS

## Troubleshooting

**Database connection error:**
- Check PostgreSQL is running
- Verify credentials in `.env`
- Ensure database exists

**Redis connection error:**
- Check Redis server is running
- Verify REDIS_URL in `.env`

**Import errors:**
- Ensure you're in the `backend` directory
- Verify virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`
