# !/usr/bin/env python
# _*_ coding:utf-8 _*_


def test_django_redis():
    # 1.导包
    from django_redis import get_redis_connection

    # 2.链接
    client = get_redis_connection('default')


    # 3. 增删改查
    client.set('django_redis_key','itcast')

    # 千万注意: 返回的是 bytes
    print(client.get('django_redis_key'))