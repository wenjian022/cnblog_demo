"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path
from django.views.static import serve

from blog import views
from cnblog import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('registered/',views.registered),
    path('logout/',views.logout),
    path('get_validCorde_img/',views.get_validCorde_img),
    path('index/',views.index),
    path('digg/',views.digg),
    path('comment/',views.comment),
    path('get_comment_tree/',views.get_comment_tree),
    # 文本编辑器上传文件的路径
    path('upload/', views.upload),

    #后台管理url
    re_path("cn_backend/$",views.cn_backend),
    re_path("cn_backend/add_article/$",views.add_article),

    re_path('^$', views.index),
    # 个人站点下的跳转
    re_path(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$',views.home_site),
    # 关于个人站点的url
    re_path('^(?P<username>\w+)$',views.home_site),
    # 文章详情页面
    re_path('^(?P<username>\w+)/articles/(?P<articles_id>\d+)$',views.article_detail),
    # 后台编辑功能
    re_path('^edit/(?P<condition>tag|category|archive)/(?P<id>\d+)',views.edit),

    # 头像
    # media配置:
    # 导入的模块
    # from django.views.static import serve
    # from cnblog import settings
    re_path(r'media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
]
