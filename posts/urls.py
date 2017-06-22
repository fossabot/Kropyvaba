from django.conf.urls import url

from .views import render_board, render_catalog, render_index, render_thread
from .views import get_media

urlpatterns = [
    url(
        r'^$',
        render_index,
        name="index"
        ),
    url(
        r'^(?P<board_name>[A-Za-z]+)/res/(?P<thread_id>[0-9]+).html$',
        render_thread,
        name="thread"
        ),
    url(
        r'^(?P<board_name>[A-Za-z]+)/$',
        render_board,
        name="board"
        ),
    url(
        r'^(?P<board_name>[A-Za-z]+)/(?P<current_page>[0-9]+).html$',
        render_board,
        name="board_page"
        ),
    url(
        r'^(?P<board_name>[A-Za-z]+)/catalog.html$',
        render_catalog,
        name="catalog"
        ),
    url(
        r'^(?P<board_name>[A-Za-z]+)/res/(?P<path>.*)$',
        get_media,
        name='media'
        ),
]
