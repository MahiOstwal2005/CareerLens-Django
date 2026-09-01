from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from analyzer.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('users/', include('users.urls')),
    path('analyzer/', include('analyzer.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
