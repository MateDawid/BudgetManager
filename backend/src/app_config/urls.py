from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

schema_view = get_schema_view(
    openapi.Info(
        title='BudgetManager API',
        default_version='v1',
        description='API for BudgetManager application.',
        contact=openapi.Contact(email='mateusiakdawid@gmail.com'),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = routers.SimpleRouter()

urlpatterns = [
    path('api/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/healthcheck', lambda r: HttpResponse()),
    path('api/admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/users/', include('app_users.urls')),
    path('api/budgets/', include('budgets.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG_TOOLBAR_ENABLED:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
