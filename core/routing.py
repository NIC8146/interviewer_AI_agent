from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/test/(?P<pk>[^/]+)/$', consumers.MyConsumer.as_asgi()),
]
