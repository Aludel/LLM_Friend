import logging

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class RefreshTokenView(APIView):
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({
                    'result': 'Refresh token is missing'
                }, status = 401)
            refresh = RefreshToken(refresh_token)
            # 注意是 ROTATE_REFRESH_TOKENS（带 S），settings.SIMPLE_JWT 里的键名如此。
            if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
                refresh.set_jti()
                response = Response({
                    'result':'success',
                    'access':str(refresh.access_token)
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
            return Response({
                'result': 'success',
                'access':str(refresh.access_token),
            })
        except Exception:
            logger.exception('刷新令牌接口异常')
            return Response({
                'result':'Refresh Token Expired',
            },status = 401)
