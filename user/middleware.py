# middleware.py
from django.contrib.auth import logout
from django.urls import reverse
from .models import userdata
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


class BlockCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if user is authenticated and if their account is blocked
        if 'email' in request.session:
            email = request.session['email']
            try:
                user = userdata.objects.get(email=email)
                if user.blocked:
                    # Log out the user
                    logout(request)
                    messages.error(request, 'Your account is blocked.')
                    # return redirect(reverse('login'))  # Redirect to login page
            except ObjectDoesNotExist:
                pass  # Handle the case where user does not exist

        return response
