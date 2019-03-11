from django.http import HttpResponse
from user.models import User, Group
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from anhomaw.util.authentications import MyTokenAuthentication
from anhomaw.util.paginations import MyNumberPagination
from anhomaw.util.permissions import MyAdminPermission, MySuperAdminPermission
from .models import User, UserToken
from .serializers import UserShowSerializer,  GroupSerializer
from .encrypt import encrypt_str
from .conf import roles
from rest_framework import status




class AuthView(APIView):
    # 登录认证
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        ret = {
            "code": 2000,
            "data": None,
            "message": None,
        }
        # print ("*"*20, request.data)
        username = request.data.get("username", None)
        passwd = request.data.get("password", None)
        if username:
            username = username.strip()
            if passwd:
                passwd = encrypt_str(username, passwd=passwd.strip())
            user_obj = User.objects.all().filter(name=username, passwd=passwd).first()
            if not user_obj:
                ret["code"] = 1005
                ret["message"] = "用户名或密码错误"
            else:
                user_alias = user_obj.alias
                user_id = user_obj.id
                user_token = encrypt_str(username.strip())
                remote_addr = request.META["REMOTE_ADDR"]
                UserToken.objects.update_or_create(name=user_obj, defaults={"token": user_token, "remote_addr": remote_addr})
                ret["data"] = {
                    "user_id": user_id,
                    "username": username.strip(),
                    "token": user_token,
                    "alias": user_alias,
                }
        else:
            ret["code"] = 1001
            ret["message"]  = "用户名不能为空"

        return Response(ret)


class UserViewSet(ModelViewSet):
    """
    用户视图集
    """
    queryset = User.objects.all()
    serializer_class = UserShowSerializer
    pagination_class = MyNumberPagination

    def create(self, request, *args, **kwargs):
        # 覆盖create 方法，处理上传数据中的 password 字段，加密后保存到数据库
        post_data = request.data
        username = post_data["name"]
        g_id = Group.objects.all().get(name=post_data["user_group"]).id
        role_id = roles.get(post_data["role"])
        passwd = encrypt_str(username, passwd=post_data["passwd"])
        post_data.update({'role': role_id, 'user_group': g_id, 'passwd': passwd})

        serializer = self.get_serializer(data=post_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # 覆盖重写 update 方法，处理上传数据中的 password，以及role／user_group等，转成数据库中的整型字段
        update_data = request.data
        if update_data.get('passwd', None):
            username = instance.name
            update_data['passwd'] = encrypt_str(username, passwd=update_data["passwd"])

        if update_data.get('role', None):
            update_data['role'] = roles.get(update_data['role'])

        if update_data.get('user_group', None):
            g_id = Group.objects.all().get(name=update_data["user_group"]).id
            update_data["user_group"] = g_id

        serializer = self.get_serializer(instance, data=update_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)




class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = MyNumberPagination
    # permission_classes = [MyAdminPermission]








