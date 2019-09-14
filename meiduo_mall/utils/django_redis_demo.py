from django_redis import get_redis_connection

def test():

    client = get_redis_connection("default")

    client.set('django_redis_key', 'itcast')

    print(client.get('django_redis_key'))