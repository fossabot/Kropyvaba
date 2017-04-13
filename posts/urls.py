from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^(?P<board_name>[A-Za-z]+)/', views.render_board, name="board"),
]
