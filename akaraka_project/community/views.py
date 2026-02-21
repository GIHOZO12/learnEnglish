from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.urls import reverse_lazy
from .models import Post, Comment, Testimony, Report, CommunityModerator
from gamification.models import Achievement


class CommunityForumView(ListView):
    """Community forum - browse posts"""
    model = Post
    template_name = 'community/forum.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True)
        
        # Filter by post type
        post_type = self.request.GET.get('type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        # Search
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))
        
        # Sort
        sort = self.request.GET.get('sort', 'new')
        if sort == 'trending':
            queryset = queryset.annotate(like_count=Count('likes')).order_by('-like_count')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        else:  # new
            queryset = queryset.order_by('-created_at')
        
        return queryset


class PostDetailView(DetailView):
    """View single post with comments"""
    model = Post
    template_name = 'community/post_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Increment view count
        post.views_count += 1
        post.save(update_fields=['views_count'])
        
        # Get comments
        context['comments'] = post.comments.filter(is_approved=True, parent_comment__isnull=True)
        context['comment_count'] = post.get_comment_count()
        context['like_count'] = post.get_like_count()
        
        # Split and clean tags
        if post.tags:
            context['tags'] = [tag.strip() for tag in post.tags.split(',') if tag.strip()]
        else:
            context['tags'] = []
        
        if self.request.user.is_authenticated:
            context['user_liked'] = post.likes.filter(id=self.request.user.id).exists()
        
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    """Create new community post"""
    model = Post
    template_name = 'community/create_post.html'
    fields = ['title', 'content', 'post_type', 'tags']
    success_url = reverse_lazy('community:forum')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post published successfully!')
        
        # Award XP
        self.request.user.add_xp(2)
        
        return super().form_valid(form)


class CreateCommentView(LoginRequiredMixin, CreateView):
    """Create comment on post"""
    model = Comment
    template_name = 'community/create_comment.html'
    fields = ['content']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, slug=self.kwargs['slug'])
        return context
    
    def form_valid(self, form):
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        form.instance.author = self.request.user
        form.instance.post = post
        messages.success(self.request, 'Comment posted!')
        
        # Award XP
        self.request.user.add_xp(1)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('community:post_detail', kwargs={'slug': self.kwargs['slug']})


class LikePostView(LoginRequiredMixin, View):
    """Like/unlike a post"""
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
            # Award XP for liking
            request.user.add_xp(1)
        
        return render(request, 'community/_post_card.html', {'post': post, 'liked': liked})


class TestimoniesView(ListView):
    """View published testimonies"""
    model = Testimony
    template_name = 'community/testimonies.html'
    context_object_name = 'testimonies'
    paginate_by = 12
    
    def get_queryset(self):
        return Testimony.objects.filter(is_published=True).annotate(
            like_count=Count('likes')
        ).order_by('-created_at')


class CreateTestimonyView(LoginRequiredMixin, CreateView):
    """Create learning testimony"""
    model = Testimony
    template_name = 'community/create_testimony.html'
    fields = ['title', 'content', 'achievement', 'rating', 'photo']
    success_url = reverse_lazy('community:testimonies')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_published = False  # Requires moderation
        messages.success(self.request, 'Testimony submitted for review!')
        return super().form_valid(form)


class ReportContentView(LoginRequiredMixin, CreateView):
    """Report inappropriate content"""
    model = Report
    template_name = 'community/report_content.html'
    fields = ['report_type', 'description']
    success_url = reverse_lazy('community:forum')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_slug = self.request.GET.get('post')
        if post_slug:
            context['post'] = get_object_or_404(Post, slug=post_slug)
        return context
    
    def form_valid(self, form):
        form.instance.reporter = self.request.user
        
        post_slug = self.request.POST.get('post')
        if post_slug:
            form.instance.reported_post = get_object_or_404(Post, slug=post_slug)
        
        messages.success(self.request, 'Report submitted. Thank you for keeping our community safe!')
        return super().form_valid(form)
