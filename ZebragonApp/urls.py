"""
URL configuration for ZebragonApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('groups/', include('groups.urls')),
    path('receipts/', include('receipts.urls')),
    path('categories/', include('categories.urls')),
    path('my_messages/', include('my_messages.urls')),
    path('profile_mangement/', include('profile_mangement.urls')),
    path('statistics/', include('statistics_and_plots.urls')),
    path('promotions/', include('promotions_and_discounts.urls')),
    path('', include('shopping_lists.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'users.views.handle404'
handler500 = 'users.views.handle500'
