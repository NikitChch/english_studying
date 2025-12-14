import logging

logger = logging.getLogger(__name__)

class DebugAuthenticationMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/reviews/'):
            print(f"\n=== DEBUG MIDDLEWARE: {request.path} ===")
            print(f"User authenticated before: {request.user.is_authenticated}")
            print(f"User: {request.user}")
            print(f"Session key: {request.session.session_key}")
            print(f"Session _auth_user_id: {request.session.get('_auth_user_id', 'Not found')}")
            print(f"Session _auth_user_hash: {request.session.get('_auth_user_hash', 'Not found')}")
            print(f"Session data: {dict(request.session)}")
        
        response = self.get_response(request)
        
        if request.path.startswith('/reviews/'):
            print(f"User authenticated after: {request.user.is_authenticated}")
            print(f"=== END DEBUG MIDDLEWARE ===\n")
        
        return response