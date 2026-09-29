from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from web.models.user import UserProfile

PASSWORD = 'pw123456'


class AccountFlowTests(TestCase):
    """登录/注册/刷新的冒烟测试。这三个接口此前各自带着一个必现故障，
    因为没有测试，全部表现为"系统异常"而无人察觉。"""

    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_and_profile(self):
        res = self.client.post(
            '/api/user/account/register/',
            {'username': 'alice', 'password': PASSWORD},
            format='json',
        )
        self.assertEqual(res.data['result'], 'success')
        self.assertEqual(res.data['username'], 'alice')
        self.assertIn('access', res.data)
        self.assertTrue(User.objects.filter(username='alice').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='alice').exists())

    def test_register_duplicate_username_is_rejected(self):
        User.objects.create_user(username='alice', password=PASSWORD)
        res = self.client.post(
            '/api/user/account/register/',
            {'username': 'alice', 'password': PASSWORD},
            format='json',
        )
        self.assertEqual(res.data['result'], '用户名已存在')

    def test_register_with_missing_field_does_not_crash(self):
        res = self.client.post('/api/user/account/register/', {}, format='json')
        self.assertEqual(res.data['result'], '用户名和密码不能为空')

    def test_login_returns_user_info(self):
        user = User.objects.create_user(username='bob', password=PASSWORD)
        UserProfile.objects.create(user=user)
        res = self.client.post(
            '/api/user/account/login/',
            {'username': 'bob', 'password': PASSWORD},
            format='json',
        )
        self.assertEqual(res.data['result'], 'success')
        self.assertEqual(res.data['user_id'], user.id)
        self.assertEqual(res.data['username'], 'bob')
        self.assertIn('access', res.data)
        self.assertIn('refresh_token', res.cookies)

    def test_login_without_profile_still_works(self):
        """createsuperuser 建的账号没有绑定 UserProfile，登录不能因此 500。"""
        User.objects.create_user(username='admin', password=PASSWORD)
        res = self.client.post(
            '/api/user/account/login/',
            {'username': 'admin', 'password': PASSWORD},
            format='json',
        )
        self.assertEqual(res.data['result'], 'success')

    def test_login_with_wrong_password(self):
        User.objects.create_user(username='bob', password=PASSWORD)
        res = self.client.post(
            '/api/user/account/login/',
            {'username': 'bob', 'password': 'wrong-password'},
            format='json',
        )
        self.assertEqual(res.data['result'], '用户名或密码错误')

    def test_refresh_token_returns_new_access(self):
        self.client.post(
            '/api/user/account/register/',
            {'username': 'carol', 'password': PASSWORD},
            format='json',
        )
        self.assertIn('refresh_token', self.client.cookies)
        res = self.client.post('/api/user/account/refresh_token/', {}, format='json')
        self.assertEqual(res.data['result'], 'success')
        self.assertIn('access', res.data)

    def test_refresh_without_cookie_is_rejected(self):
        res = self.client.post('/api/user/account/refresh_token/', {}, format='json')
        self.assertEqual(res.status_code, 401)


class DefaultPhotoTests(TestCase):
    def test_default_photo_points_at_an_existing_file(self):
        """本次 404 的回归测试：模型里 default 写的路径必须真实存在。
        之前写的是 'user.photos/default.png'（点号），文件却在 media/user/photos/，
        于是每个新注册用户的头像 URL 都是 404。"""
        user = User.objects.create_user(username='dave', password=PASSWORD)
        profile = UserProfile.objects.create(user=user)
        self.assertTrue(
            profile.photo.storage.exists(profile.photo.name),
            f'默认头像文件不存在：{profile.photo.name}',
        )

    def test_default_and_upload_share_the_same_directory(self):
        """default 和 upload_to 必须同树，否则默认头像和上传的照片会散在两处。"""
        user = User.objects.create_user(username='erin', password=PASSWORD)
        profile = UserProfile.objects.create(user=user)
        self.assertTrue(profile.photo.name.startswith('user/photos/'))
