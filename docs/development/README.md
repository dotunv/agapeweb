# Developer Onboarding Guide

This guide is designed to help new developers get started with the Agape subscription management system. It covers the setup process, coding standards, development workflow, and other important information for contributing to the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Environment](#development-environment)
4. [Coding Standards](#coding-standards)
5. [Development Workflow](#development-workflow)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Common Tasks](#common-tasks)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- Git
- PostgreSQL (recommended for production, SQLite is fine for development)
- A virtual environment tool (venv, virtualenv, or conda)

### Clone the Repository

```bash
git clone <repository-url>
cd agape
```

### Set Up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # For development
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Run Migrations

```bash
python manage.py migrate
```

### Create a Superuser

```bash
python manage.py createsuperuser
```

### Run the Development Server

```bash
python manage.py runserver
```

The server will be available at http://localhost:8000/

## Project Structure

The Agape project is organized into the following main components:

### Core Apps

- **agape**: The main project configuration
- **core**: Core functionality shared across the project
- **users**: User management and authentication
- **subscriptions**: Subscription plans, user subscriptions, queues, wallets, and referrals
- **transactions**: Financial transactions and withdrawal requests

### Key Directories

- **docs**: Project documentation
- **scripts**: Utility scripts for development and deployment
- **static**: Static files (CSS, JavaScript, images)
- **templates**: HTML templates
- **logs**: Log files

## Development Environment

### Recommended Tools

- **IDE**: Visual Studio Code or PyCharm
- **Database Tool**: pgAdmin (for PostgreSQL) or DB Browser for SQLite
- **API Testing**: Postman or Insomnia
- **Version Control**: Git with GitHub or GitLab

### Useful Extensions for VS Code

- Python
- Django
- Pylance
- Black Formatter
- ESLint
- GitLens

### Debugging

To debug the application:

1. Add breakpoints in your code using `import pdb; pdb.set_trace()` or use your IDE's debugging tools
2. Run the server in debug mode
3. Access the endpoint that triggers the code you want to debug

## Coding Standards

### Python Style Guide

We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code with some modifications:

- Use 4 spaces for indentation
- Maximum line length is 100 characters
- Use docstrings for all public modules, functions, classes, and methods
- Use type hints for function parameters and return values

### Django Best Practices

- Follow the [Django coding style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- Use Django's ORM for database operations
- Write reusable apps and components
- Keep views simple and focused on a single task
- Use Django's built-in security features

### Code Formatting

We use the following tools to maintain code quality:

- **Black**: For automatic code formatting
- **Flake8**: For linting
- **isort**: For sorting imports

These tools are configured in the `pyproject.toml` file and can be run using pre-commit hooks.

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality before committing changes. To set up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Development Workflow

### Branching Strategy

We follow a simplified Git flow branching strategy:

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/feature-name**: Feature branches
- **bugfix/bug-name**: Bug fix branches
- **hotfix/fix-name**: Urgent fixes for production

### Pull Request Process

1. Create a new branch from `develop` for your feature or bug fix
2. Make your changes and commit them with descriptive commit messages
3. Push your branch to the remote repository
4. Create a pull request to merge your branch into `develop`
5. Ensure all tests pass and code quality checks succeed
6. Request a code review from at least one team member
7. Address any feedback from the code review
8. Once approved, merge your pull request

### Code Review Guidelines

When reviewing code, consider the following:

- Does the code follow our coding standards?
- Is the code well-documented?
- Are there appropriate tests?
- Is the code efficient and maintainable?
- Does the code introduce any security vulnerabilities?

## Testing

### Running Tests

To run the test suite:

```bash
python manage.py test
```

To run tests for a specific app:

```bash
python manage.py test app_name
```

To run a specific test:

```bash
python manage.py test app_name.tests.TestClass.test_method
```

### Writing Tests

We use Django's testing framework for writing tests. Each app should have a `tests.py` file or a `tests` directory with test modules.

Test classes should inherit from `django.test.TestCase` for tests that require database access, or `django.test.SimpleTestCase` for tests that don't.

Example test:

```python
from django.test import TestCase
from users.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("testpassword123"))
```

### Test Coverage

We aim for high test coverage. To check test coverage:

```bash
coverage run --source='.' manage.py test
coverage report
```

## Documentation

### Code Documentation

- Use docstrings for all public modules, functions, classes, and methods
- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstring format
- Include type hints for function parameters and return values

Example:

```python
def process_payment(self, from_subscription: 'Subscription', amount: Decimal) -> bool:
    """
    Process a payment from another subscription.

    Args:
        from_subscription: The subscription making the payment
        amount: The amount to be paid

    Returns:
        bool: True if the payment was successful, False otherwise

    Raises:
        ValueError: If the amount is negative or zero
    """
    # Implementation
```

### Project Documentation

Project documentation is stored in the `docs` directory and includes:

- API documentation
- Database schema and relationships
- Developer onboarding guide (this document)
- Deployment process
- User manual for admin interface
- Security practices and policies
- Troubleshooting guide
- Testing strategy and procedures
- Architecture diagrams
- Third-party integrations

## Common Tasks

### Adding a New Model

1. Create the model in the appropriate app's `models.py` file
2. Add docstrings and type hints
3. Create migrations: `python manage.py makemigrations`
4. Apply migrations: `python manage.py migrate`
5. Register the model in the app's `admin.py` file
6. Create serializers in the app's `serializers.py` file
7. Create views in the app's `views.py` file
8. Add URL patterns in the app's `urls.py` file
9. Write tests for the model

### Adding a New API Endpoint

1. Create or update the view in the app's `views.py` file
2. Add URL patterns in the app's `urls.py` file
3. Update API documentation
4. Write tests for the endpoint

### Database Migrations

For detailed information about database migrations, see [Database Migrations Versioning Strategy](../migrations.md).

### Debugging Common Issues

- **Migration errors**: Check for circular dependencies or missing fields
- **Import errors**: Check for typos or missing packages
- **Permission errors**: Check user permissions and authentication
- **Database errors**: Check database connection and model constraints

For more detailed troubleshooting, see the [Troubleshooting Guide](../troubleshooting/README.md).