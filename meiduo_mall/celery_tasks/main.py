# !/usr/bin/env python
# _*_ coding:utf-8 _*_

# 1.导包
from celery import Celery

# 2.配置celery可能加载到的美多项目的包
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")


# 2.实例化对象
app = Celery('celery_tasks')

# 3.配置 消息队列 的位置
app.config_from_object('celery_tasks.config')

# 4.自动查找任务
app.autodiscover_tasks(['celery_tasks.sms'])

# 5. 记得在终端开启  异步服务