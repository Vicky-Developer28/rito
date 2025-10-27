from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from unfold.admin import ModelAdmin
from unfold.decorators import display
from django.utils.html import format_html
from django.urls import reverse

# Register your models here.
from .models import (
    Device, RitoAccount, SocialMediaAccount, ContactMessage, 
    Subscriber, CommunityMember, Topic, Question, Answer, 
    Comment, Space, SpaceQuestion, Notification, Bookmark
)

# Unregister default models
admin.site.unregister(User)
admin.site.unregister(Group)

# ========== CUSTOM ADMIN CONFIGS ==========

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name", "is_staff", "is_superuser", "date_joined"]
    list_filter = ["is_staff", "is_superuser", "is_active", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-date_joined"]

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

# ========== MAIN APP MODELS ==========

@admin.register(Device)
class DeviceAdmin(ModelAdmin):
    list_display = ["ieda_short", "mac_address", "is_active", "registered_at"]
    list_filter = ["is_active", "registered_at"]
    search_fields = ["ieda", "mac_address"]
    readonly_fields = ["registered_at"]
    
    @display(description="IEDA")
    def ieda_short(self, obj):
        return f"{obj.ieda[:12]}..." if len(obj.ieda) > 12 else obj.ieda

@admin.register(RitoAccount)
class RitoAccountAdmin(ModelAdmin):
    list_display = ["rito_id", "user_link", "device_link", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["rito_id", "user__username", "device__ieda"]
    readonly_fields = ["rito_id", "created_at"]
    
    @display(description="User")
    def user_link(self, obj):
        if obj.user:
            url = reverse("admin:auth_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "No User"
    
    @display(description="Device")
    def device_link(self, obj):
        if obj.device:
            url = reverse("admin:main_device_change", args=[obj.device.id])
            return format_html('<a href="{}">{}</a>', url, obj.device.ieda_short())
        return "No Device"

@admin.register(SocialMediaAccount)
class SocialMediaAccountAdmin(ModelAdmin):
    list_display = ["platform", "username", "rito_account_link", "created_at"]
    list_filter = ["platform", "created_at"]
    search_fields = ["username", "platform_id", "rito_account__rito_id"]
    readonly_fields = ["created_at"]
    
    @display(description="Rito Account")
    def rito_account_link(self, obj):
        url = reverse("admin:main_ritoaccount_change", args=[obj.rito_account.id])
        return format_html('<a href="{}">{}</a>', url, obj.rito_account.rito_id)

@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ["name", "email", "subject_short", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["created_at"]
    list_editable = ["is_read"]
    
    @display(description="Subject")
    def subject_short(self, obj):
        return obj.subject[:50] + "..." if len(obj.subject) > 50 else obj.subject

@admin.register(Subscriber)
class SubscriberAdmin(ModelAdmin):
    list_display = ["email", "is_active", "subscribed_at"]
    list_filter = ["is_active", "subscribed_at"]
    search_fields = ["email"]
    readonly_fields = ["subscribed_at"]
    list_editable = ["is_active"]

# ========== COMMUNITY MODELS ==========

@admin.register(CommunityMember)
class CommunityMemberAdmin(ModelAdmin):
    list_display = ["name", "user_id", "email", "membership_type", "reputation_score", "is_active", "join_date"]
    list_filter = ["membership_type", "is_active", "join_date"]
    search_fields = ["name", "email", "user_id", "interests"]
    readonly_fields = ["user_id", "join_date"]
    list_editable = ["is_active"]
    
    @display(description="User ID")
    def user_id(self, obj):
        return obj.user_id

@admin.register(Topic)
class TopicAdmin(ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["slug", "created_at"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ["name"]}

@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ["title_short", "author_link", "views", "is_active", "created_at"]
    list_filter = ["is_active", "is_anonymous", "created_at", "topics"]
    search_fields = ["title", "content", "author__name"]
    readonly_fields = ["slug", "created_at", "updated_at"]
    list_editable = ["is_active"]
    filter_horizontal = ["topics"]
    
    @display(description="Title")
    def title_short(self, obj):
        return obj.title[:60] + "..." if len(obj.title) > 60 else obj.title
    
    @display(description="Author")
    def author_link(self, obj):
        url = reverse("admin:main_communitymember_change", args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.name)

@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_display = ["question_short", "author_link", "is_accepted", "is_active", "created_at"]
    list_filter = ["is_active", "is_accepted", "is_anonymous", "created_at"]
    search_fields = ["content", "question__title", "author__name"]
    readonly_fields = ["created_at", "updated_at"]
    list_editable = ["is_active", "is_accepted"]
    
    @display(description="Question")
    def question_short(self, obj):
        title = obj.question.title
        return title[:50] + "..." if len(title) > 50 else title
    
    @display(description="Author")
    def author_link(self, obj):
        url = reverse("admin:main_communitymember_change", args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.name)

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ["content_short", "author_link", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["content", "author__name", "answer__question__title"]
    readonly_fields = ["created_at", "updated_at"]
    list_editable = ["is_active"]
    
    @display(description="Comment")
    def content_short(self, obj):
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content
    
    @display(description="Author")
    def author_link(self, obj):
        url = reverse("admin:main_communitymember_change", args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.name)

@admin.register(Space)
class SpaceAdmin(ModelAdmin):
    list_display = ["name", "slug", "created_by_link", "is_public", "is_active", "created_at"]
    list_filter = ["is_public", "is_active", "created_at"]
    search_fields = ["name", "description", "created_by__name"]
    readonly_fields = ["slug", "created_at"]
    list_editable = ["is_public", "is_active"]
    filter_horizontal = ["members", "moderators", "topics"]
    prepopulated_fields = {"slug": ["name"]}
    
    @display(description="Creator")
    def created_by_link(self, obj):
        url = reverse("admin:main_communitymember_change", args=[obj.created_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.created_by.name)

@admin.register(SpaceQuestion)
class SpaceQuestionAdmin(ModelAdmin):
    list_display = ["question_short", "space_link", "posted_by_link", "posted_at"]
    list_filter = ["posted_at", "space"]
    search_fields = ["question__title", "space__name", "posted_by__name"]
    readonly_fields = ["posted_at"]
    
    @display(description="Question")
    def question_short(self, obj):
        title = obj.question.title
        return title[:50] + "..." if len(title) > 50 else title
    
    @display(description="Space")
    def space_link(self, obj):
        url = reverse("admin:main_space_change", args=[obj.space.id])
        return format_html('<a href="{}">{}</a>', url, obj.space.name)
    
    @display(description="Posted By")
    def posted_by_link(self, obj):
        url = reverse("admin:main_communitymember_change", args=[obj.posted_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.posted_by.name)

@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ["recipient_link", "actor_link", "verb", "is_read", "created_at"]
    list_filter = ["verb", "is_read", "created_at"]
    search_fields = ["recipient__name", "actor__name"]
    readonly_fields = ["created_at"]
    list_editable = ["is_read"]
    
    @display(description="Recipient")
    def recipient_link(self, obj):
        url = reverse("admin:main_communitymember_change", args=[obj.recipient.id])
        return format_html('<a href="{}">{}</a>', url, obj.recipient.name)
    
    @display(description="Actor")
    def actor_link(self, obj):
        url = reverse("admin:main_communitymember_change", args=[obj.actor.id])
        return format_html('<a href="{}">{}</a>', url, obj.actor.name)

@admin.register(Bookmark)
class BookmarkAdmin(ModelAdmin):
    list_display = ["user_link", "question_short", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__name", "question__title"]
    readonly_fields = ["created_at"]
    
    @display(description="User")
    def user_link(self, obj):
        url = reverse("admin:main_communitymember_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.name)
    
    @display(description="Question")
    def question_short(self, obj):
        title = obj.question.title
        return title[:60] + "..." if len(title) > 60 else title