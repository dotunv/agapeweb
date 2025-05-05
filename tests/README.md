# Agape Application Tests

This directory contains tests for the Agape application. The tests are organized into different categories to ensure comprehensive coverage of the application's functionality.

## Test Categories

### 1. UI Tests

UI tests use Django's test client to test the user interface and interactions. These tests are located in `frontend/ui_tests.py`.

### 2. Use Case Tests

Use case tests cover complete user journeys and business processes. These tests are located in `frontend/use_case_tests.py`.

### 3. Selenium Tests

Selenium tests use browser automation to test JavaScript interactions and complex UI flows. These tests are located in `frontend/selenium_tests.py`.

## Running the Tests

### Prerequisites

- Python 3.8+
- Django 5.2+
- Selenium 4.18.1+
- Chrome WebDriver (for Selenium tests)

### Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. For Selenium tests, install Chrome and ChromeDriver:

```bash
# On Ubuntu/Debian
apt-get update
apt-get install -y google-chrome-stable
apt-get install -y chromium-driver

# On macOS
brew install --cask google-chrome
brew install --cask chromedriver
```

### Running All Tests

To run all tests:

```bash
python manage.py test
```

### Running Specific Test Categories

To run UI tests:

```bash
python manage.py test frontend.ui_tests
```

To run use case tests:

```bash
python manage.py test frontend.use_case_tests
```

To run Selenium tests:

```bash
python manage.py test frontend.selenium_tests
```

### Running Individual Test Classes or Methods

To run a specific test class:

```bash
python manage.py test frontend.ui_tests.HomePageTests
```

To run a specific test method:

```bash
python manage.py test frontend.ui_tests.HomePageTests.test_home_page_loads
```

## Test Coverage

To generate a test coverage report:

1. Install coverage:

```bash
pip install coverage
```

2. Run the tests with coverage:

```bash
coverage run --source='.' manage.py test
```

3. Generate the coverage report:

```bash
coverage report
```

4. For an HTML report:

```bash
coverage html
```

Then open `htmlcov/index.html` in your browser.

## Continuous Integration

These tests are designed to be run in a CI/CD pipeline. The Selenium tests can be run in headless mode, which is suitable for CI environments.

## Writing New Tests

When writing new tests, follow these guidelines:

1. UI tests should focus on template rendering and basic user interactions.
2. Use case tests should cover complete business processes and user journeys.
3. Selenium tests should be used for JavaScript interactions and complex UI flows.
4. All tests should be independent and not rely on the state of other tests.
5. Use appropriate assertions to verify the expected behavior.
6. Use descriptive test method names that clearly indicate what is being tested.
7. Add comments to explain complex test logic.

## Test Data

Test data is created in the `setUp` method of each test class. This ensures that each test has a clean environment to work with.

## Mocking

For tests that involve external services or APIs, use Django's mocking capabilities to simulate the external service's behavior.

Example:

```python
from unittest.mock import patch

@patch('module.external_service')
def test_external_service(self, mock_service):
    mock_service.return_value = {'status': 'success'}
    # Test code that uses the external service
```

