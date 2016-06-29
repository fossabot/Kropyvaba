"""kropyvaba URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin

from tastypie.api import Api
from posts.api.resources import PostResource, BoardResource

v1_api = Api(api_name='v1')
v1_api.register(PostResource())
v1_api.register(BoardResource())
urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^i18n/', include('django.conf.urls.i18n')),
	url(r'^api/', include(v1_api.urls)),
	url(r'^', include('posts.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
