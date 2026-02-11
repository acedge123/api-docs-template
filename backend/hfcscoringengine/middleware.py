"""
Monitoring middleware for request tracking and performance monitoring.
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class MonitoringMiddleware(MiddlewareMixin):
    """
    Middleware for monitoring request performance and logging.
    """

    def process_request(self, request):
        """Start timing the request."""
        request.start_time = time.time()

        # Log request details
        logger.info(
            f"Request started: {request.method} {request.path} "
            f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')}"
        )

    def process_response(self, request, response):
        """Log response details and timing."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time

            # Log response details
            logger.info(
                f"Request completed: {request.method} {request.path} "
                f"Status: {response.status_code} "
                f"Duration: {duration:.3f}s"
            )

            # Add performance headers
            response['X-Request-Duration'] = f"{duration:.3f}"

            # Log slow requests
            if duration > 1.0:  # More than 1 second
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.3f}s"
                )

        return response

    def process_exception(self, request, exception):
        """Log exceptions."""
        duration = time.time() - request.start_time if hasattr(request, 'start_time') else 0

        logger.error(
            f"Request failed: {request.method} {request.path} "
            f"Exception: {type(exception).__name__}: {str(exception)} "
            f"Duration: {duration:.3f}s"
        )

        # Return a JSON error response for API requests
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Internal server error',
                'message': str(exception) if hasattr(exception, '__str__') else 'Unknown error'
            }, status=500)


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware for security monitoring and logging.
    """

    def process_request(self, request):
        """Monitor for potential security issues."""
        # Log suspicious requests
        suspicious_patterns = [
            '/admin/',  # Admin access attempts
            'sqlmap',   # SQL injection tools
            'union select',  # SQL injection attempts
            '<script',  # XSS attempts
            'javascript:',  # XSS attempts
        ]

        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        path = request.path.lower()
        query_string = request.META.get('QUERY_STRING', '').lower()

        for pattern in suspicious_patterns:
            if (pattern in user_agent or
                pattern in path or
                pattern in query_string):
                logger.warning(
                    f"Suspicious request detected: {request.method} {request.path} "
                    f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
                    f"User-Agent: {user_agent}"
                )
                break

        # Log authentication attempts
        if request.path.startswith('/api/') and request.method == 'POST':
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header:
                logger.warning(
                    f"Unauthenticated API request: {request.method} {request.path} "
                    f"from {request.META.get('REMOTE_ADDR', 'unknown')}"
                )

    def process_response(self, request, response):
        """Add security headers."""
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response
