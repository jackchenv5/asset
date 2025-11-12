from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BarcodeSummaryViewSet

router = DefaultRouter()
router.register(r'barcode-summaries', BarcodeSummaryViewSet, basename='barcode-summary')

urlpatterns = [
    path('', include(router.urls)),
]