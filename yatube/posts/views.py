from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


def index(request):
    posts_list = Post.objects.order_by('-pub_date').select_related('author', 'group').prefetch_related(
        'comments')
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
    posts_group = Post.objects.filter(group=group).order_by('-pub_date').select_related(
        'author', 'group').prefetch_related('comments')
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
    following = is_subscribed(request.user, profile)
    posts = Post.objects.filter(author__username=username).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following_count = profile.following.count()
    follower_count = profile.follower.count()
    return render(request, 'profile.html', {
        'profile': profile, 'posts': posts, 'page': page, 'paginator': paginator,
        'following': following, 'follower_count': follower_count, 'following_count': following_count
    })


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post__id=post_id)
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


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user).order_by('-pub_date').select_related(
        'author', 'group').prefetch_related('comments')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page, 'paginator': paginator, 'posts': posts})


def is_subscribed(user, author):
    if user.is_authenticated:
        return Follow.objects.filter(user=user, author=author).exists()


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if request.user != author and not is_subscribed(request.user, author):
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    if request.user != author and is_subscribed(request.user, author):
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)
