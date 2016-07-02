from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^(?P<board_name>[a-z]+)/$', views.ret_board, name='board'), #return a first page
	url(r'^(?P<board_name>[a-z]+)/catalog$', views.ret_board_with_catalog, name='board'),
	url(r'^(?P<board_name>[a-z]+)/(?P<page_num>[0-9]+)/$', views.ret_board_page, name='board'),
	url(r'^post-(?P<post_id>[0-9]+)/$', views.ret_post, name='post'),
	url(r'^(?P<board_name>[a-z]+)/res/(?P<post_id>[0-9]+)/$', views.ret_post_legacy, name='post'), #link legacy mode for compatibility with wakaba-like boards
]