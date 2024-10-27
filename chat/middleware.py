# myapp/middleware.py
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

class IdleLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Get the last activity time
            last_activity = request.session.get('last_activity')

            # If last_activity is in string format, convert it back to datetime
            if isinstance(last_activity, str):
                last_activity = timezone.datetime.fromisoformat(last_activity)

            # Calculate idle time
            if last_activity:
                idle_time = (timezone.now() - last_activity).total_seconds()
                if idle_time > settings.SESSION_COOKIE_AGE:
                    # Logout the user if idle time exceeds session age
                    logout(request)
                    return redirect('chat:login')  # Change 'login' to your login URL name

            # Update last activity time as a string
            request.session['last_activity'] = timezone.now().isoformat()

        return self.get_response(request)



class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude specific paths (like login, logout)
        if not request.user.is_authenticated and request.path not in [settings.LOGIN_URL, '/accounts/logout/']:
            return redirect(settings.LOGIN_URL)  # Redirect to login page if not authenticated
        return self.get_response(request)
