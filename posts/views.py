from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from .models import Board, ThreadPost, Post
from .forms import PostForm, ThreadForm

def index(request):
	board_list = Board.objects.all()
	return render(request, 'posts/index.html', {'board_list': board_list})

def ret_post(request, post_id, board_name = None, three_slash = 0):
	this_post = Post.objects.filter(id = post_id)
	if len(this_post) == 0:
		this_post = Post.objects.filter(id = 1)
		return HttpResponseRedirect('/post-'+str(this_post[0].id)) #if post with requested id dont exist, return to post with id 1
	else:
		board_list = Board.objects.all()
		curr_board = board_list.filter(id = this_post[0].board.id) #
		board_list = Board.objects.order_by('name')
		if this_post[0].thread != 0:
			topic = ThreadPost.objects.filter(op__id = this_post[0].thread)
			return HttpResponseRedirect('/post-'+str(topic[0].id)+'#'+str(this_post[0].id))
		else:
			topic = ThreadPost.objects.filter(op__id = this_post[0].id)
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
					return HttpResponseRedirect('/post-'+str(new_post.id))
		else:
			post_form = PostForm()
	return render(request, 'posts/post.html', {'three_slash' : three_slash,'curr_board' : curr_board, 'board_list': board_list, 'topic' : topic[0], 'post_form': post_form, 'posts_list': posts_list})

def ret_post_legacy(request, post_id, board_name):
	three_slash = 1
	return ret_post(request, post_id, board_name, three_slash)
	
def ret_board_with_catalog(request, board_name):
	two_slash = 1
	return ret_board(request, board_name, two_slash)

def ret_board_page(request, board_name, page_num):
	two_slash = 1
	return ret_board(request, board_name, page_num, two_slash)
	
def ret_board(request, board_name, page_num = 0, two_slash = 0):
	board_list = Board.objects.filter(name = board_name)
	board_id = board_list[0].id
	all_post = Post.objects.filter(board = board_id)
	topics_list = ThreadPost.objects.filter(op__board__id = board_id).order_by('op__pub_date').reverse()
	posts_list = Post.objects.exclude(thread = 0).order_by('-id')
	board_list = Board.objects.order_by('name')
	curr_board = board_list.filter(id = board_id)
	if request.method == 'POST':
		'''post_form = PostForm(request.POST, request.FILES)
		if post_form.is_valid():
			new_post = post_form.save(commit=False)
			if len(new_post.author) != 0 or len(new_post.body) != 0 or len(request.FILES) != 0:
				if len(new_post.author) == 0:
					new_post.author = 'Хтось'
				new_post.pub_date = timezone.now()
				new_post.board = curr_board[0]
				new_post.save()
				return HttpResponseRedirect('/'+str(board_name)+'/')'''
		thread_form = ThreadForm(request.POST, request.FILES)
		if thread_form.is_valid():
			if len(thread_form.cleaned_data['theme']) != 0:
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
	next = int(page_num)+1
	prev = int(page_num)-1
	last = round(len(topics_list)/12) #number of all pages
	topics_list = topics_list[(12*int(page_num)):(12*int(page_num)+12)]
	return render(request, 'posts/board.html', {'two_slash' : two_slash, 'next' : next, 'prev' : prev, 'current': int(page_num), 'last' : last, 'curr_board': curr_board,'board_list': board_list, 'thread_form': thread_form, 'topics_list': topics_list, 'posts_list': posts_list})