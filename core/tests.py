from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from django.db.utils import OperationalError

class HealthCheckTests(TestCase):
    """
    Test suite for the health check endpoint
    """

    def setUp(self):
        """
        Set up the test client
        """
        self.client = APIClient()
        self.url = reverse('health-check')

    def test_health_check_success(self):
        """
        Test that the health check endpoint returns a successful response
        when everything is working properly
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertEqual(response.data['database'], 'healthy')
        self.assertIn('timestamp', response.data)
        self.assertIn('details', response.data)
        self.assertIn('api_version', response.data['details'])
        self.assertIn('environment', response.data['details'])

    @patch('core.views.connections')
    def test_health_check_database_error(self, mock_connections):
        """
        Test that the health check endpoint correctly reports database issues
        """
        # Configure the mock to raise an OperationalError when cursor() is called
        mock_conn = mock_connections.__getitem__.return_value
        mock_conn.cursor.side_effect = OperationalError("Database connection error")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unhealthy')
        self.assertEqual(response.data['database'], 'unhealthy')
