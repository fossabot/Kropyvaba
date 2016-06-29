from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from .models import Board, ThreadPost, Post
from .forms import PostForm, ThreadForm

def index(request):
	board_list = Board.objects.all()
	return render(request, 'posts/index.html', {'board_list': board_list})

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
	if request.method == 'POST': #work with forms.
		post_form = PostForm(request.POST, request.FILES)
		if post_form.is_valid():
			new_post = post_form.save(commit=False)
			if len(new_post.author) != 0 or len(new_post.body) != 0 or len(request.FILES) != 0:
				if len(new_post.author) == 0:
					new_post.author = 'Хтось'
				new_post.pub_date = timezone.now()
				new_post.board = curr_board[0]
				new_post.save()
				return HttpResponseRedirect('/post-'+str(post_id))
	else:
		post_form = PostForm()
	return render(request, 'posts/post.html', {'board_list': board_list, 'topic' : topic[0], 'post_form': post_form, 'posts_list': posts_list})

def ret_board(request, board_name):
	board_list = Board.objects.filter(name = board_name)
	board_id = board_list[0].id
	"""all_post = Post.objects.filter(board = board_id)
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
	posts_list = temp_list"""
	board_list = Board.objects.order_by('description')
	curr_board = board_list.filter(id = board_id)
	"""for topic in topics_list:
		for post in all_post:
			if post.thread == topic.id:
				topic.posts +=1
		topic.posts -=3"""
	if request.method == 'POST':
		post_form = PostForm(request.POST, request.FILES)
		if post_form.is_valid():
			new_post = post_form.save(commit=False)
			if len(new_post.author) != 0 or len(new_post.body) != 0 or len(request.FILES) != 0:
				if len(new_post.author) == 0:
					new_post.author = 'Хтось'
				new_post.pub_date = timezone.now()
				new_post.board = curr_board[0]
				new_post.save()
				return HttpResponseRedirect('/'+str(board_name))
		thread_form = ThreadForm(request.POST, request.FILES)
		if thread_form.is_valid():
			if len(request.FILES) != 0 and len(thread_form.cleaned_data['theme']) != 0:
				n_author = thread_form.cleaned_data['author']
				n_theme = thread_form.cleaned_data['theme']
				n_thread = thread_form.cleaned_data['thread']
				n_body = thread_form.cleaned_data['body']
				n_file = request.FILES['file']
				if len(n_author) == 0:
					n_author = 'Хтось'
				n_pub_date = timezone.now()
				n_board = curr_board[0]
				n_op = Post(author = n_author, pub_date = n_pub_date, thread = n_thread, board = n_board, body = n_body, file = n_file)
				n_op.save()
				new_thread = ThreadPost(op = n_op, theme = n_theme)
				new_thread.save()
				return HttpResponseRedirect('/post-'+str(new_thread.id))
			else:
				print("file or theme are not assigned")
		else:
			print("form invalid")
	else:
		post_form = PostForm()
		thread_form = ThreadForm()
	#topics_list = topics_list[:12]
	#return render(request,  'posts/board.html', {'curr_board': curr_board,'board_list': board_list, 'thread_form': thread_form, 'topics_list': topics_list, 'posts_list': posts_list})
	return render(request, 'posts/board.html', {'curr_board': curr_board,'board_list': board_list, 'thread_form': thread_form, 'post_form': post_form})