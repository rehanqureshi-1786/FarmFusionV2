# FarmFusion Backend

AI-powered agriculture platform FastAPI backend.

## Features

- JWT Authentication with refresh tokens
- Crop management and recommendations
- Animal detection with image upload
- Labour services marketplace
- Live mandi (market) prices
- Product store with orders
- Financial services (extensible)
- Background tasks with Celery
- Redis caching

## Tech Stack

- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Pydantic v2
- JWT Authentication
- Redis
- Celery
- Docker

## Setup

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database and update `.env` file.

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Docker Setup

1. Build and run with docker-compose:
```bash
docker-compose up --build
```

2. Access API at `http://localhost:8000`
3. API docs at `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user
- `PATCH /api/v1/auth/me` - Update profile
- `POST /api/v1/auth/change-password` - Change password

### Crops
- `GET /api/v1/crops` - List crops
- `POST /api/v1/crops` - Create crop
- `GET /api/v1/crops/{id}` - Get crop
- `PATCH /api/v1/crops/{id}` - Update crop
- `DELETE /api/v1/crops/{id}` - Delete crop
- `POST /api/v1/crops/recommend` - Get AI recommendations

### Mandi Prices
- `GET /api/v1/mandi/prices` - Get prices
- `GET /api/v1/mandi/prices/trend/{commodity}` - Price trends
- `GET /api/v1/mandi/commodities` - List commodities
- `GET /api/v1/mandi/markets` - List markets

### Labour
- `GET /api/v1/labour/requests` - List requests
- `POST /api/v1/labour/requests` - Create request
- `POST /api/v1/labour/requests/{id}/apply` - Apply for job

### Products
- `GET /api/v1/products` - List products
- `POST /api/v1/products` - Create product
- `POST /api/v1/products/{id}/order` - Place order
- `GET /api/v1/products/orders/my` - My orders

### Animal Detection
- `POST /api/v1/animals/detect` - Upload image for detection
- `GET /api/v1/animals/detections` - List detections

## Environment Variables

See `.env` file for all required variables.

## Architecture

```
backend/
├── app/
│   ├── api/         # API routes
│   ├── core/        # Config, security
│   ├── db/          # Database setup
│   ├── models/      # SQLAlchemy models
│   ├── schemas/     # Pydantic schemas
│   ├── services/    # Business logic
│   └── main.py      # App entry
```
