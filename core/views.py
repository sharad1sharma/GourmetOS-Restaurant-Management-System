from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User


@ensure_csrf_cookie
def dashboard_view(request):
    """Renders the main Restaurant Management System Dashboard web app UI."""
    return render(request, 'index.html')


class UserRegisterView(APIView):
    """API endpoint allowing users to register new accounts."""
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({
            'message': f'Account "{user.username}" created successfully!',
            'username': user.username
        }, status=status.HTTP_201_CREATED)

