from django.urls import path, include
from .views import (
    CreateUserView, LoginView, UpdatePassword, MeView
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)

router.register("create-user", CreateUserView, 'create user')
router.register("login", LoginView, 'login')
router.register("update-passwor", UpdatePassword, 'update password')
router.register("me", MeView, 'me')

urlpatterns = [
    path("", include(router.urls))
]
