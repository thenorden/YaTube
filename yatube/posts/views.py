from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .models import Post, Group, User, Comment
from .forms import PostForm, CommentForm


def index(request):
    posts_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_group = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(posts_group, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    title = 'Новый пост'
    btn_caption = 'Опубликовать'
    form = PostForm()
    return render(request, 'new_post.html', {'form': form, 'title': title, 'btn_caption': btn_caption})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author__username=username).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'profile': profile, 'posts': posts, 'page': page, 'paginator': paginator})


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post__id=post_id, author__username=username)
    form = CommentForm()
    return render(request, 'post.html', {'profile': profile, 'post': post, 'comments': comments, 'form': form})


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    title = 'Редактировать запись'
    btn_caption = 'Сохранить'
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'new_post.html', {'title': title, 'btn_caption': btn_caption, 'form': form, 'post': post})


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'comments.html', {'form': form, 'post': post})
