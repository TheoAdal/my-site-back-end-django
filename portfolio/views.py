import json
from django.http import JsonResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .utilities.send_email import send_verification_email
import uuid

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
            if not(name and username and email and password):
                return JsonResponse({
                    "message": "MISSING_FIELDS",
                    "code": "Missing fields"
                }, status=400)
            
            # email check 
            if User.objects.filter(email=email).exists():
                return JsonResponse({"message": "Email already registered", "code": "EMAIL_ALREADY_REGISTERED"}, status=409)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({"message": "Username is taken", "code": "USERNAME_ALREADY_REGISTERED"}, status=409)
            
            # create user # create_user() instead of create(), to hash password
            user = User.objects.create_user(name=name, 
                    username=username, 
                    email=email, 
                    password=password, 
                    is_verified=False,
                    verification_token=uuid.uuid4(),
                    verification_token_expiry=timezone.now() + timedelta(hours=1)
                    )
            
            # send email
            send_verification_email(user)
            
            return JsonResponse({
                "message": "User registered successfully. Please check your email to verify.",
                "code": "USER_REGISTERED_EMAIL_SENT",
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "email": user.email,
                
            }, status=200)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Invalid request method",
                    "code": "INVALID_REQUEST_METHOD"}, status=405)


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
                
            #check if email is verified   
            if not user.is_verified:
                return JsonResponse({
                    "message": "Please verify your email before logging in.",
                    "code": "EMAIL_NOT_VERIFIED"
                }, status=403)
                
            #Authenticate using username (Django auth requirements)
            user = authenticate(username=user.username, password=password)
 
            if user is not None:
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

#LOGOUT
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
    
#VERIFY     
@csrf_exempt
def verify_user(request, token):
    if request.method == "GET":
        try:
            user = User.objects.get(verification_token=token)

            if user.is_verified:
                return JsonResponse({"message": "User already verified", "code": "USER_ALREADY_VERIFIED"}, status=200)

            if user.verification_token_expiry < timezone.now():
                return JsonResponse({"message": "Verification link expired", "code": "LINK_EXPIRED"}, status=400)

            user.is_verified = True
            user.verification_token = None
            user.verification_token_expiry = None
            user.save()

            return JsonResponse({"message": "Email verified successfully", "code": "EMAIL_VERIFIED"}, status=200)

        except User.DoesNotExist:
            return JsonResponse({"message": "Invalid verification token", "code": "INVALID_VERIFICATION_TOKEN"}, status=400)

    return JsonResponse({"message": "Invalid request method", "code": "INVALID_REQUEST_METHOD"}, status=405)


@csrf_exempt
def resend_verification(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            email = data.get("email")
            
            #email field check
            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({"message": "User not found", "code":"USER_NOT_FOUND"}, status=404)

            if user.is_verified:
                return JsonResponse({"message": "User already verified", "code": "USER_ALREADY_VERIFIED"}, status=200)

            # generate new token & expiry
            user.verification_token = uuid.uuid4()
            user.verification_token_expiry = timezone.now() + timedelta(hours=1)
            user.save()

            verification_link = f"http://localhost:3000/api/verify/{user.verification_token}/"

            # send email
            send_verification_email(user)

            return JsonResponse({"message": "A new verification email has been sent."}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)
