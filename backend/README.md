# FarmFusion Backend

AI-powered agriculture platform FastAPI backend.

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL** - Primary database
- **Pydantic v2** - Data validation
- **JWT** - Authentication
- **Redis** - Caching & message broker
- **Celery** - Background tasks
- **Docker** - Containerization

## Quick Start

### Using Docker (Recommended)

```bash
docker-compose up --build
```

Access API at http://localhost:8000

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup PostgreSQL and update `.env`

4. Run migrations:
```bash
alembic upgrade head
```

5. Start server:
```bash
python run.py
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (OAuth2)
- `GET /api/v1/auth/me` - Get current user

### Crops
- `GET /api/v1/crops` - List crops
- `POST /api/v1/crops` - Create crop
- `GET /api/v1/crops/{id}` - Get crop
- `PATCH /api/v1/crops/{id}` - Update crop
- `POST /api/v1/crops/recommend` - AI crop recommendations

## Project Structure

```
backend/
├── app/
│   ├── api/v1/         # API routes
│   ├── core/           # Config, security
│   ├── db/             # Database setup
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── main.py         # App entry
├── alembic/            # Database migrations
├── docker-compose.yml  # Docker orchestration
├── Dockerfile          # Container definition
└── requirements.txt    # Python dependencies
```

## Environment Variables

See `.env` file for all available options.
