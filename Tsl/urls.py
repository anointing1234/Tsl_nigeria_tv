from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.static import serve 



urlpatterns = [
    path('',views.home,name='home'),
    path('home/',views.home,name='home'),
    path('live_tv/',views.live_tv,name='live_tv'),
    path('ondemand/',views.ondemand,name='ondemand'),
    path('contact/',views.contact,name='contact'),
    path('About/',views.About,name='About'),
    path('login/',views.login,name='login'),
    path('Signup/',views.signup,name='Signup'),
    path('send_password/',views.send_pass,name='send_password'),
    path('reset_pass',views.reset_pass,name='reset_pass'),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]