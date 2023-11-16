from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (ListView,
                                  DetailView,
                                  UpdateView,
                                  DeleteView,
                                  CreateView)

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, ProfileEditForm
from .utils import count_comments

User = get_user_model()

POST_TO_SHOW = 10


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POST_TO_SHOW
    ordering = '-pub_date'
    model = count_comments(Post.published_objects, 'comments')

    def get_queryset(self):
        return (Post.objects.select_related(
                'author',
                'location',
                'category').
                filter(is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()).
                annotate(comment_count=Count('comments')).
                order_by('-pub_date'))


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.filter(
            slug=category_slug,
            is_published=True))
    post_list = (Post.published_objects.all().
                 filter(category=category).
                 annotate(comment_count=Count('comments')).
                 order_by('-pub_date'))
    paginator = Paginator(post_list, POST_TO_SHOW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html',
                  {'category': category,
                   'page_obj': page_obj})


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=CommentForm(),
            comments=self.object.comments.select_related('author')
        )

    def get_object(self, queryset=None):
        if self.request.user and self.request.user.is_authenticated:
            return get_object_or_404(
                Post.objects.filter(
                    Q(is_published=True)
                    | Q(author=self.request.user)
                ),
                pk=self.kwargs[self.pk_url_kwarg])
        else:
            return get_object_or_404(Post.published_objects,
                                     pk=self.kwargs[self.pk_url_kwarg])


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POST_TO_SHOW

    def get_queryset(self):
        return (self.model.objects.
                select_related('author').
                filter(author__username=self.kwargs['username']).
                annotate(comment_count=Count('comments')).
                order_by('-pub_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            args=[self.request.user.username])


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form: PostForm):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            args=[self.request.user.username])


class PostMixin(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        return get_object_or_404(Post.objects.all(),
                                 pk=self.kwargs[self.pk_url_kwarg])

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if post.author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            args=[self.kwargs['post_id']])


class PostDeleteView(PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            args=[self.request.user.username])


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid:
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment,
                                    pk=kwargs[self.pk_url_kwarg])
        if comment.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            args=[self.kwargs['post_id']])


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    ...
