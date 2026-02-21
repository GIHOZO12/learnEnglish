from django.contrib import admin
from .models import Post, Comment, Testimony, Report, CommunityModerator


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'is_published', 'is_featured', 'views_count', 'created_at')
    list_filter = ('post_type', 'is_published', 'is_featured', 'is_pinned', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    actions = ['mark_featured', 'mark_pinned']
    
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
    
    def mark_pinned(self, request, queryset):
        queryset.update(is_pinned=True)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author__username', 'post__title', 'content')
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(Testimony)
class TestimonyAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_published', 'created_at')
    list_filter = ('rating', 'is_published', 'created_at')
    search_fields = ('user__username', 'title', 'content')
    actions = ['publish_testimonies']
    
    def publish_testimonies(self, request, queryset):
        queryset.update(is_published=True)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'report_type', 'status', 'created_at', 'reviewed_by')
    list_filter = ('report_type', 'status', 'created_at')
    search_fields = ('reporter__username', 'description')
    readonly_fields = ('created_at',)


@admin.register(CommunityModerator)
class CommunityModeratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'appointed_at', 'reports_handled')
    list_filter = ('is_active', 'appointed_at')
    search_fields = ('user__username',)
