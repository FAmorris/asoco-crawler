"""json管理器 URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import RedirectView

import main.views

# 路由
urlpatterns = [
    url(r'^admin', admin.site.urls),
    url(r'^$', main.views.admin),
    url(r'^manage', main.views.admin),
    url(r'^files', main.views.files),
    url(r'^doUse', main.views.do_use),
    url(r'^doNotUse', main.views.do_no_use),
    url(r'^edit/(.+)$', main.views.edit),
    url(r'^readContent', main.views.read_content),
    url(r'^delete', main.views.delete),
    url(r'^addfile', main.views.addfile),
    url(r'^savefile', main.views.savefile),
    url(r'^config', main.views.config),
    url(r'^setCrawlInterval$', main.views.setCrawlInterval),
    url(r'^seelog', main.views.seelog),
    url(r'^weibo', main.views.weibo_page),
    url(r'^do_use_weibo', main.views.do_use_weibo),
    url(r'^do_not_use_weibo', main.views.do_not_use_weibo),
    url(r'^favicon.ico', RedirectView.as_view(url="/static/images/gerapy.png"))
]
