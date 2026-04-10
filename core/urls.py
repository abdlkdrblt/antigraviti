"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include

from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('', include('diet.urls')),
]

# Canlı sunucuda (Render) Persistent Disk üzerindeki medyaları sunmak için
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
