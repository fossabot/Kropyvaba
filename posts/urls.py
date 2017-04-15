from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^(?P<board_name>[A-Za-z]+)/res/(?P<thread_id>[0-9]+).html', views.render_thread, name="thread"),
    url(r'^(?P<board_name>[A-Za-z]+)/', views.render_board, name="board"),  
]
