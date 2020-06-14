from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year,
                             publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)  # Список активных комментариев для этой статьи.
    new_comment = None
    comment_form = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)  # Пользователь отправил комментарий.
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)  # Создаем комментарий, но пока не сохраняем в базе данных.
            new_comment.post = post  # Привязываем комментарий к текущей статье.
            new_comment.save()  # Сохраняем комментарий в базе данных.
        else:
            comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form})


def post_share(request, post_id):
    # Получение статьи по идентификатору.
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Форма была отправлена на сохранение.
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Все поля формы прошли валидацию.
            cd = form.cleaned_data
            # ... Отправка электронной почты.
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            subject = f"{cd['name']} ({cd['email']}) recommends you reading '{post.title}'"
            # message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            message = f"Read '{post.title}' at {post_url}\n\n{cd['name']}\'s comments:{cd['comments']}"
            send_mail(subject, message, 'aksemary@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
