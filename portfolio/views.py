from django.shortcuts import render
import json
from django.http import JsonResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import AllowAny

from .models import User

# Create your views here.

#Before applying "AllowAny", we wrote this code below before a route:
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])

# GET ALL USERS
def get_all_users(request):
    if request.method == "GET":
        users = User.objects.all().values("id", "name", "username", "email")
        return JsonResponse(list(users), safe=False)
        # return Response(list(users))


#REGISTER
@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt 
def register_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            name = data.get("name")
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            
            # blank field check
            if not(name and username and email):
                return JsonResponse({"error": "Missing fields"}, status=400)
            
            # create user # create_user() instead of create(), to hash password
            user = User.objects.create_user(name=name, username=username, email=email, password=password)
            
            return JsonResponse({
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "email": user.email
            }, status=201)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


#LOGIN
@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt 
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            email = data.get("email")
            password = data.get("password")
            
            #check blank fields
            if not (email and password):
                return JsonResponse({"error": "Missing fields"}, status=400)
            
            #find user email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({
                    "message": "Invalid credentials",
                    "code": "INVALID_CREDENTIALS"
                }, status=401)
                
            #Authenticate using username (Django auth requirements)
            user = authenticate(username=user.username, password=password)
 
            if check_password(password, user.password):
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    "message": "Login successful",
                    "code": "LOGIN_SUCCESSFUL",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "name": user.name
                    },
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh)
                    }
                })
            else:
                return JsonResponse({
                    "message": "Invalid credentials",
                    "code": "INVALID_CREDENTIALS"
                }, status=401)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Invalid request method",
                    "code": "INVALID_REQUEST_METHOD"}, status=405)

#Logout
@api_view(["POST"])
@permission_classes([AllowAny])
def logout_user(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful"}, status=205)
    except TokenError:
        return Response({"error": "Invalid or expired token"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)