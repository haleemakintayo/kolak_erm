"""
URL configuration for kolak project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from users.auth_views import (
    CustomTokenObtainPairView,
    UserProfileView,
    ChangePasswordView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication routes
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/auth/me/', UserProfileView.as_view(), name='auth_me'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='auth_change_password'),

    # App API routes
    path('api/patients/', include('patients.urls')),
    path('api/users/', include('users.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/billing/', include('billing.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
