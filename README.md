# Agape - Subscription Management System

A Django-based subscription management system with a modern API-first architecture.

## Features

- User authentication and authorization using Knox
- Subscription plan management
- Payment processing
- Transaction tracking
- Queue-based contribution system
- Admin interface with custom styling
- API documentation with Swagger UI and ReDoc
- CORS support for frontend integration
- Environment-based configuration

## Prerequisites

- Python 3.8+
- PostgreSQL (recommended for production)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd agape
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # For development
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Raw Schema: http://localhost:8000/api/schema/

## Admin Interface

The admin interface is available at http://localhost:8000/admin/

## Development

### Running Tests
```bash
python manage.py test
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## Production Deployment

1. Set `DJANGO_DEBUG=False` in your `.env` file
2. Configure your database URL in `.env`
3. Set up a proper web server (e.g., Nginx)
4. Use Gunicorn as the application server:
```bash
gunicorn agape.wsgi:application
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 