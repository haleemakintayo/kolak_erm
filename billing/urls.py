from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HMOProviderViewSet, PatientHMOEnrollmentViewSet

router = DefaultRouter()
router.register(r'hmo-providers', HMOProviderViewSet, basename='hmo-provider')
router.register(r'enrollments', PatientHMOEnrollmentViewSet, basename='patient-hmo-enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
