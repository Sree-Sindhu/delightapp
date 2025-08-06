from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/orders/<int:order_id>/tracking/", consumers.OrderTrackingConsumer.as_asgi()),
]
