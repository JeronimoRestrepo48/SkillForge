"""
URL configuration for SkillForge project.
All endpoints in English. Root (/) = login; all other routes require authentication.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.api import MeView
from catalog.api import (
    CourseRateView,
    CourseListAPIView,
    CourseDetailAPIView,
    CourseModulesAPIView,
    CategoryListAPIView,
)
from transactions.api import CheckoutQuoteV1APIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('core.urls')),
    path('courses/', include('catalog.urls')),
    path('cart/', include('transactions.urls')),
    path('my-account/', include('users.urls')),
    # OpenAPI / Swagger UI (JWT: use Authorize with Bearer <access>)
    path(
        'api/schema/',
        SpectacularAPIView.as_view(permission_classes=[AllowAny], authentication_classes=[]),
        name='schema',
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            url_name='schema',
            permission_classes=[AllowAny],
            authentication_classes=[],
        ),
        name='swagger-ui',
    ),
    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # REST API
    path('api/me/', MeView.as_view(), name='api_me'),
    path('api/categories/', CategoryListAPIView.as_view(), name='api_category_list'),
    path('api/courses/', CourseListAPIView.as_view(), name='api_course_list'),
    path('api/courses/<int:pk>/', CourseDetailAPIView.as_view(), name='api_course_detail'),
    path('api/courses/<int:pk>/modules/', CourseModulesAPIView.as_view(), name='api_course_modules'),
    path('api/courses/<int:pk>/rate/', CourseRateView.as_view(), name='api_course_rate'),
    path('api/v1/checkout/quote/', CheckoutQuoteV1APIView.as_view(), name='api_v1_checkout_quote'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
