
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user.models import UserToken
from anhomaw.settings import REST_FRAMEWORK
import datetime

class MyTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 获取token
        token = request.query_params.get("token", None)
        token_obj = UserToken.objects.all().filter(token=token).first()
        if not token_obj:
            raise AuthenticationFailed("Authenticate failed.")

        # 设置token过期时间
        token_time = token_obj.token_time.replace(tzinfo=None)
        now = datetime.datetime.now()
        interval_seconds = (now-token_time).total_seconds()
        if interval_seconds > REST_FRAMEWORK['DEFAULT_AUTHENTICATION_TOKEN_EXPIRE']:
            raise AuthenticationFailed("Token expired.")

        return (token_obj.name, token_obj)


    def authenticate_header(self, request):
        pass