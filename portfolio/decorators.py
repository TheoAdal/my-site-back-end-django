from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from functools import wraps

def public_api(methods):
    """
    Decorator for public API routes.
    Usage: @public_api(["POST", "GET"])
    """
    def decorator(func):
        decorated_view = api_view(methods)(permission_classes([AllowAny])(func))
        return decorated_view
    return decorator

def private_api(methods):
    """
    Decorator for private API routes (requires authentication).
    Usage: @private_api(["GET", "PATCH"])
    """
    def decorator(func):
        decorated_view = api_view(methods)(permission_classes([IsAuthenticated])(func))
        return decorated_view
    return decorator
