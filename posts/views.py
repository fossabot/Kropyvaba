from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from .models import Board, Post
from .forms import PostForm

def index(request): #nuff said
	return render(request, 'posts/index.html', {})

def ret_post(request, post_id):
	this_post = Post.objects.filter(id = post_id)
	if len(this_post) == 0:
	    this_post = Post.objects.filter(id = 1)
	board_list = Board.objects.all()
	curr_board = board_list.filter(id = this_post[0].board.id)
	if this_post[0].thread != 0:
		topic = Post.objects.filter(id = this_post[0].thread)
	else:
		topic = Post.objects.filter(id = this_post[0].id)
		this_post = 0
	posts_list = Post.objects.filter(thread = topic[0].id)
	if request.method == 'POST': #work with forms. #TODO make a two form for posts and threads
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			new_post = form.save(commit=False)
			if len(new_post.author) != 0 or len(new_post.body) != 0 or len(request.FILES) != 0:
				if len(new_post.author) == 0:
					new_post.author = 'Хтось'
				new_post.pub_date = timezone.now()
				new_post.board = curr_board[0]
				new_post.save()
				return HttpResponseRedirect('/post-'+str(post_id))
	else:
		form = PostForm()
	return render(request, 'posts/post.html', {'board_list': board_list, 'topic' : topic[0], 'form': form, 'posts_list': posts_list})

def ret_board(request, board_name):
	board_list = Board.objects.filter(name = board_name)
	board_id = board_list[0].id
	all_post = Post.objects.filter(board = board_id)
	temp_list = all_post.order_by('-pub_date')
	topics_list = []
	for post in temp_list:
		unik = True
		if post.thread == 0:
			reply = post.id
		else:
			reply = post.thread
		for topic in topics_list:
			if reply != topic.id and unik == True:
				unik = True
			else:
				unik = False
				break
		if unik == True:
			temp = Post.objects.filter(id = reply)
			topics_list.append(temp[0])
	posts_list = Post.objects.exclude(thread = 0).order_by('-id')
	temp_list = []
	for topic in topics_list:
	    temp = 0
	    for post in posts_list:
	        if post.thread == topic.id and temp <= 5:
	            temp_list.append(post)
	            temp+=1
	posts_list = temp_list
	board_list = Board.objects.order_by('description')
	curr_board = board_list.filter(id = board_id)
	for topic in topics_list:
		for post in all_post:
			if post.thread == topic.id:
				topic.posts +=1
		topic.posts -=3
	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			new_post = form.save(commit=False)
			if len(new_post.author) != 0 or len(new_post.body) != 0 or len(request.FILES) != 0:
				if len(new_post.author) == 0:
					new_post.author = 'Хтось'
				new_post.pub_date = timezone.now()
				new_post.board = curr_board[0]
				new_post.save()
				if new_post.thread == 0:
				    return HttpResponseRedirect('/post-'+str(new_post.id))
				return HttpResponseRedirect('/'+str(board_name))
	else:
		form = PostForm()
	topics_list = topics_list[:12]
	return render(request,  'posts/board.html', {'curr_board': curr_board,'board_list': board_list,'form': form, 'topics_list': topics_list, 'posts_list': posts_list})