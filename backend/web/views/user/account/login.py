import logging

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from web.models.user import UserProfile

logger = logging.getLogger(__name__)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username', '').strip()
            password = request.data.get('password', '').strip()
            if not username or not password:
                return Response({
                    'result': '用户名与密码不能为空',
                })

            user = authenticate(request, username=username, password=password)

            if user:
                # UserProfile.user 没写 related_name，反向访问器是 user.userprofile 而非
                # user.profile，所以必须显式取。get_or_create 是为了兜住 createsuperuser
                # 建的管理员账号——它没有绑定的 UserProfile，直接 get 会 500。
                user_profile, _ = UserProfile.objects.get_or_create(user=user)
                refresh = RefreshToken.for_user(user)
                response = Response({
                    'result':'success',
                    'access':str(refresh.access_token),
                    'user_id':user.id,
                    'username':user.username,
                    'photo':user_profile.photo.url,
                    'profile':user_profile.profile,
                })
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    samesite='Lax',
                    secure=True,
                    max_age=86400 * 7,
                )
                return response
            else:
                return Response({
                    'result': '用户名或密码错误',
                })


        except Exception:
            # 裸 except 会把代码错误伪装成"系统异常"，排查时毫无线索，所以必须落日志。
            logger.exception('登录接口异常')
            return Response({
                'result': '系统异常，请稍后重试',
            })
