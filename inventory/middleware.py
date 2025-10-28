# inventory/middleware.py

import threading

_request_storage = threading.local()

class RequestMiddleware:
    """
    Middleware to store the current request object in a thread-local variable.
    This allows us to access the request (and thus the logged-in user)
    from anywhere in the application, which is crucial for our signal handlers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_storage.request = request
        response = self.get_response(request)
        if hasattr(_request_storage, 'request'):
            del _request_storage.request
        return response

def get_current_request():
    """Helper to safely retrieve the current request object."""
    return getattr(_request_storage, 'request', None)

def get_current_user():
    """Helper to safely retrieve the current authenticated user."""
    request = get_current_request()
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None