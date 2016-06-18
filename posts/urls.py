from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^(?P<board_name>[a-z]+)/$', views.ret_board, name='board'),
	url(r'^post-(?P<post_id>[0-9]+)/$', views.ret_post, name='post'),
]