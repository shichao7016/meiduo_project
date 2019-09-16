# 1.导包
from django.contrib.auth.backends import ModelBackend

# 2.继承 类
from apps.users.models import User
import re

from meiduo_mall.settings.dev import logger


# 封装校验用户名的函数
def get_user_by_account(account):
    try:
        if re.match('^1[345789]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)

    except User.DoesNotExist:
        logger.error('用户对象不存在')
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):

        # 3. 实现多账号 校验用户名和 手机号
        user = get_user_by_account(username)

        # 校验密码是否正确
        if user and user.check_password(password):
            return user


# 4. dev 配置
