from django.urls import path
from . import views

urlpatterns = [
    path("getallusers_public/", views.get_all_users_public, name="get_all_users_public"), #PUBLIC:  get all users
    path("getallusers_private/", views.get_all_users_private, name="get_all_users_private"), #PRIVATE: get all users
    path("register/", views.register_user, name="register_user"), # register user (added email verification)
    path("login/", views.login_user,name="login_user"), # login user (added is_verified)
    path("logout/", views.logout_user, name="logout_user"), # logout user
    path("verify/<uuid:token>/", views.verify_user, name="verify"), # verify route
    path("resend-verification/", views.resend_verification, name="resend_verification"), #resend verification email
    path("forgot-password/", views.forgot_password, name="forgot-password"), #send reset password link
    path("reset-password/<uuid:token>/", views.reset_password, name="reset-password"), #reset password
    path("update/profile/", views.update_profile, name="update_profile"), # update user
]
