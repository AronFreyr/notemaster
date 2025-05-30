"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.generic.base import TemplateView

from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notemaster/', include('notes.urls')),
    path('taskmaster/', include('taskmaster.urls')),
    path('timemaster/', include('timemaster.urls')),
    path('logbook/', include('logbook.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('notemaster/xml/', include('xml_converter.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('', TemplateView.as_view(template_name='registration/login.html'), name='login_screen')
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
