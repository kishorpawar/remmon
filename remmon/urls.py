"""remmon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url, include
from django.conf.urls.static import static 
from django.conf import settings
from django.contrib import admin


from rest_framework import routers

from servers import views


router = routers.DefaultRouter()

router.register(r'servers', views.ServerViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'enroll/server/$', views.EnrollView.as_view(), name='enroll-server'),
    url(r'^', include(router.urls)),

    url(r'^server/uptime/$', views.uptime, name='uptime'),
    url(r'^server/memory/$', views.memusage, name='memusage'),
    url(r'^server/cpuusage/$', views.cpuusage, name='cpuusage'),
    url(r'^server/getdisk/$', views.getdisk, name='getdisk'),
    url(r'^server/getusers/$', views.getusers, name='getusers'),
    url(r'^server/getips/$', views.getips, name='getips'),
    url(r'^server/gettraffic/$', views.gettraffic, name='gettraffic'),
    url(r'^server/proc/$', views.getproc, name='getproc'),
    url(r'^server/getdiskio/$', views.getdiskio, name='getdiskio'),
    url(r'^server/getcpus/([\w\-\.]+)/$', views.getcpus, name='getcpus'),
    url(r'^server/getnetstat/$', views.getnetstat, name='getnetstat'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
