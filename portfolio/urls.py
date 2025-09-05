from django.urls import path
from . import views

urlpatterns = [
    path("getallusers/", views.get_all_users, name="get_all_users"), #get all users
    path("register/", views.register_user, name="register_user"), # register user (added email verification)
    path("login/", views.login_user,name="login_user"), # login user (added is_verified)
    path("logout/", views.logout_user, name="logout_user"), # logout user
    path("verify/<uuid:token>/", views.verify_user, name="verify"), # verify route
    path("resend-verification/", views.resend_verification, name="resend_verification"), #resend verification email
]
