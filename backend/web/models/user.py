import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now, localtime


# 上传目录与下面的 default 必须同树，否则默认头像和用户上传的照片会散在两个目录里。
def photo_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    return f'user/photos/{instance.user_id}_{filename}'



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 相对 MEDIA_ROOT 的路径，对应 media/user/photos/default.png。
    photo = models.ImageField(default='user/photos/default.png', upload_to=photo_upload_to)
    profile = models.TextField(default='此时无声胜有声', max_length=500)
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.user.username} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}'
