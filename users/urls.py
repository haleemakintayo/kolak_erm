from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    DoctorViewSet,
    RoleViewSet,
    DepartmentViewSet,
    PermissionViewSet,
)

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
