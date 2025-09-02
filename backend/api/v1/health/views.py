from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError

def health_check(request):
    """Simple health check endpoint for Railway"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except OperationalError:
        db_status = "unhealthy"
    
    return JsonResponse({
        "status": "ok",
        "database": db_status,
        "message": "Django app is running"
    })
