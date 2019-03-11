from django.urls import path, re_path
from . import views


urlpatterns = [
    path('auth/', views.AuthView.as_view()),

    re_path('^users/(?P<pk>\d+)/$', views.UserViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update', 'delete': 'destroy'})),
    path('users/', views.UserViewSet.as_view({'get': 'list', 'post': 'create'})),

    re_path('^groups/(?P<pk>\d+)/$', views.GroupViewSet.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update', 'patch': 'partial_update'})),
    path('groups/', views.GroupViewSet.as_view({'get': 'list', 'post': 'create'})),

]

