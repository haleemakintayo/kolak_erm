from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, QueueEntryViewSet

router = DefaultRouter()
router.register(r'queue', QueueEntryViewSet, basename='queue-entry')
router.register(r'', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
