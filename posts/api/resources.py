from tastypie.resources import ModelResource
from posts.models import Post, Board


class PostResource(ModelResource):
    class Meta:
        queryset = Post.objects.all().reverse()
        allowed_methods = ['get']

class BoardResource(ModelResource):
    class Meta:
        queryset = Board.objects.all().reverse()
        allowed_methods = ['get']