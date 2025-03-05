"""
URL configuration for upick project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from .views import HomeView

urlpatterns = [
    path('', login_required(HomeView.as_view()), name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include(('apps.authentication.urls', 'authentication'), namespace='authentication')),
    path('schedule/', include('apps.schedule.urls')),
    path('plants/', include('apps.plants.urls')),
    path('produce/', include(('apps.produceplanner.urls', 'produceplanner'), namespace='produceplanner')),
    path('planning/', include(('apps.planning.urls', 'planning'), namespace='planning')),
    path('beneficials/', include(('apps.beneficials.urls', 'beneficials'), namespace='beneficials')),
    path('covercrops/',include(('apps.covercrops.urls','covercdrops'),namespace='covercrops')),
    path('log/',include(('apps.log.urls','log'),namespace='log')),
    path('foliarrecipes/',include(('apps.foliarrecipes.urls','foliarrecipes'),namespace='foliarrecipes')),
    path('reminders/', include(('apps.reminders.urls', 'reminders'), namespace='reminders')),
    path('minerals/', include(('apps.minerals.urls', 'minerals'), namespace='minerals')),
    path('help/', include(('apps.help.urls', 'help'), namespace='help')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)