"""ai_artcritic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from hello.views import myView # import myView function from views.py in hello directory
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from critic.views import criticView, addCritic, deleteCritic, aboutView, contactView, classifyEra, classifyMood, analyzeValue, analyzeColor, random_test

urlpatterns = [
    path('', lambda req: redirect('/home/')),
    path('admin/', admin.site.urls),
    path('sayHello/', myView),
    path('home/', criticView),
    path('addCritic/', addCritic),
    path('deleteCritic/<int:critic_id>/', deleteCritic),
    path('critic/', classifyEra),
    path('classifyMood/', classifyMood),
    path('analyzeValue/', analyzeValue),
    path('analyzeColor/', analyzeColor),
    path('about/', aboutView),
    path('contact/', contactView),
    path('random_test/', random_test, name="random_test"),
]
if settings.DEBUG:
    urlpatterns += static (settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)