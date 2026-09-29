import logging

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from web.models.user import UserProfile

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    def post(self, request):
        # request.data.get() 在缺 key 时返回 None，直接 .strip() 会 AttributeError
        username = (request.data.get('username') or '').strip()
        password = (request.data.get('password') or '').strip()
        if not username or not password:
            return Response({
                'result': '用户名和密码不能为空'
            })
        if User.objects.filter(username=username).exists():
            return Response({
                'result': '用户名已存在'
            })

        try:
            # 建用户、建 profile、签发 token 三者必须同生共死。否则 token 签发一旦失败，
            # 用户已经落库、前端却收到"系统异常"，用户再注册一次只会得到"用户名已存在"，
            # 而那个账号的密码是他以为没注册成功的那次设的。
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password)
                user_profile = UserProfile.objects.create(user=user)
                refresh = RefreshToken.for_user(user)
        except Exception:
            logger.exception('注册接口异常')
            return Response({
                'result': '系统异常，请稍后重试'
            })

        response = Response({
            'result': 'success',
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'photo': user_profile.photo.url,
            'profile': user_profile.profile,
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
