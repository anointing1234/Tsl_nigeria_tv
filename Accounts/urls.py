from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from Accounts import views
from django.views.static import serve 



urlpatterns = [
    path('register_view/', views.register_view, name='register_view'),
    path('Logout/',views.logout_view, name='Logout'),
    path('login_view/',views.login_views, name='login_view'),
    path('send_password_reset/',views.send_password_reset_code,name='send_password_reset'),
    path('reset_password/',views.reset_password,name='reset_password'),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]