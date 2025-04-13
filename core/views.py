from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connections
from django.db.utils import OperationalError
from datetime import datetime

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint to verify API status and database connection
    """
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'healthy',
        'details': {
            'api_version': '1.0.0',
            'environment': 'development',
        }
    }

    # Check database connection
    try:
        db_conn = connections['default']
        db_conn.cursor()
    except OperationalError:
        health_status['status'] = 'unhealthy'
        health_status['database'] = 'unhealthy'
    
    return Response(health_status)
