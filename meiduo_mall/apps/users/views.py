from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
import re

from django_redis import get_redis_connection

from apps.users.models import User
from utils.response_code import RETCODE
from django.contrib.auth.mixins import LoginRequiredMixin


# 6. 用户中心
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_info.html')


# 5.退出
class LogOutView(View):
    def get(self, request):
        # 1.清除 登录状态 session
        from django.contrib.auth import logout
        logout(request)
        # 2.清除 username --- cookie
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')
        # 3.重定向到首页
        return response


# 4.登录
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 1.后台接收 解析参数 :3个参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 2. form表单  非表单 ,headers
        # 3. 校验 判空判正则

        # 4. 判断用户名 和密码是否正确--orm User.objects.get(username=username,password=passwod)
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)

        # 判断 user是否存在 不存在 代表登录失败
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 保持登登录状态login()
        login(request, user)

        # 判断是否记住登录
        if remembered != 'on':
            #     不记住--会话结束 失效了
            request.session.set_expiry(0)
        else:
            # 记住--2星期
            request.session.set_expiry(None)

        # 操作 next
        next = request.GET.get('next')

        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))

        # 存用户名到 cookie 里面去
        response.set_cookie('username', user.username, max_age=2 * 14 * 24 * 3600)

        # 5.跳转到首页
        return response


# 3.手机号
class MobileCountView(View):
    def get(self, request, mobile):
        # 1.接收参数

        # 2.校验 是否为空 正则

        # 3.务逻辑判断-- 数据库有没有--返回count
        count = User.objects.filter(mobile=mobile).count()

        # 4.返回响应对象
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 2.判断用户名是否重复
class UsernameCountView(View):
    def get(self, request, username):
        # 1.接收参数

        # 2.校验 是否为空 正则

        # 3.务逻辑判断-- 数据库有没有--返回count
        count = User.objects.filter(username=username).count()

        # 4.返回响应对象
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 1.注册视图
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 1.接收参数 contrl + option(alt) + 单击
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 2.校验 --判空--正则
        if not all([username, password, password2, mobile]):
            return http.HttpResponseForbidden('缺少参数!')

        # 3.用户名:正则校验—判断重复
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户')

        # 4. 密码:正则校验
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20个数字字母')

        # 5. 两次是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入不一致!')

        # 6.手机号 正则——判断重复
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('手机号格式有误')

        # 7.是否勾选同意
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选同意!')

        # 判断短信验证码 是否正确
        sms_code = request.POST.get('msg_code')

        redis_sms_client = get_redis_connection('sms_code')
        redis_sms_code = redis_sms_client.get('sms_%s' % mobile)

        if not redis_sms_code:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        redis_sms_client.delete('sms_%s' % mobile)

        if sms_code != redis_sms_code.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码不正确!'})

        # 3. 注册
        from apps.users.models import User
        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 4. 保持登录状态
        from django.contrib.auth import login
        login(request, user)

        # 4.重定向
        return redirect(reverse('contents:index'))





        # 1.GET—注册页面显示  templates
        # 2.POST 注册功能
        # 判断是否为空!
        # 3.用户名:正则校验—判断重复
        # 4. 密码:正则校验
        # 5. 两次是否一致
        # 6.手机号 正则——判断重复
        # 7.是否勾选同意
        #
        # 8.注册功能 —>入库—mysql—orm—模型类—数据迁移
        # 			    ——>密码—加密解密—>
        # 				django自带权限认证 —User
        #
        # web开发流程
        # 1.先建立模型类—数据迁移
        # 2.接收参数—request.POST
        # 3.校验(非正常用户: 抓包软件filddler charls,postman,爬虫,ajax)
        # 4.注册功能
        # 5.跳转首页 重定向redirect()
