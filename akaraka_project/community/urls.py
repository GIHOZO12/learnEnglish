from django.urls import path
from .views import (
    CommunityForumView, PostDetailView, CreatePostView, CreateCommentView,
    LikePostView, TestimoniesView, CreateTestimonyView, ReportContentView
)

app_name = 'community'

urlpatterns = [
    path('forum/', CommunityForumView.as_view(), name='forum'),
    path('post/create/', CreatePostView.as_view(), name='create_post'),
    path('post/<slug:slug>/comment/', CreateCommentView.as_view(), name='create_comment'),
    path('post/<slug:slug>/like/', LikePostView.as_view(), name='like_post'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('testimonies/', TestimoniesView.as_view(), name='testimonies'),
    path('testimonies/create/', CreateTestimonyView.as_view(), name='create_testimony'),
    path('report/', ReportContentView.as_view(), name='report_content'),
]
