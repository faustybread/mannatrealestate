"""
URL configuration for luxury_realestate project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('portal/', include('portal.urls', namespace='portal')),
    path('', include('properties.urls', namespace='properties')),
]

# Serve user-uploaded media (property photos). WhiteNoise handles /static/, but
# not /media/, so we serve it through Django. This runs in DEBUG locally and on
# Vercel (where there's no separate media server) — fine for a demo.
if settings.DEBUG or getattr(settings, 'ON_VERCEL', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
