from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path('^host/(?P<pk>\d+)/$', views.HostViewSet.as_view({'delete': 'destroy', 'put': 'update', 'get': 'retrieve'})),
    path('host/', views.HostViewSet.as_view({'get': 'list', 'post': 'create'})),

    re_path('^group/(?P<pk>\d+)/$', views.GroupVewSet.as_view({'delete': 'destroy', 'put': 'update', 'get': 'retrieve'})),
    path('group/', views.GroupVewSet.as_view({'get': 'list', 'post': 'create'})),

    path('checkhost/', views.CheckHost.as_view()),   # 检查主机是否存在
    path('copykey/',  views.CopyPrivateKey.as_view()),  # 拷贝服务器公钥到被控端
    path('adhoc/',  views.AdHocView.as_view()),    # ansible 远程指令执行
    path('hostbatch/', views.HostBatchView.as_view()),   # 上传文件，批量添加主机
    # path('listfd/', views.ListFdView.as_view()),    # 获取账号本身的 ansible 资源目录
    # path('playbook/', views.PlayBookView.as_view()),  # roles  playbook
]