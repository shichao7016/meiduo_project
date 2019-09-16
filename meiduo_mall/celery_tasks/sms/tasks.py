# !/usr/bin/env python
# _*_ coding:utf-8 _*_

from celery_tasks.main import app
from libs.yuntongxun.sms import CCP


@app.task
def send_sms_code_ccp(mobile, sms_code):

    # 手机号    6位码 过期时间分钟   短信模板
    result = CCP().send_template_sms(mobile, [sms_code, 5], 1)

    print(sms_code)

    return result
