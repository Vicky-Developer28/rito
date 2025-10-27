from django.db import models
import uuid
import random
import string
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models
import uuid
import random
import string
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
import json

def generate_rito_id():
    timestamp = str(int(timezone.now().timestamp()))
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"RITO-{timestamp[-6:]}-{random_str}"

def generate_registration_code():
    """Generate a 6-digit registration code"""
    return ''.join(random.choices(string.digits, k=6))

class Device(models.Model):
    ieda = models.CharField(max_length=64, unique=True)
    mac_address = models.CharField(max_length=17, unique=True)
    registration_code = models.CharField(max_length=6, default=generate_registration_code)
    registered_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Device {self.ieda[:8]}..."
    
    def update_location(self, ip_address=None):
        """Update device location based on IP address"""
        if not ip_address:
            return
            
        self.ip_address = ip_address
        try:
            # Using ipapi.co for location data (free tier available)
            response = requests.get(f'http://ipapi.co/{ip_address}/json/')
            if response.status_code == 200:
                data = response.json()
                self.latitude = data.get('latitude')
                self.longitude = data.get('longitude')
                self.city = data.get('city', '')
                self.country = data.get('country_name', '')
                self.save()
        except Exception as e:
            print(f"Location update failed: {e}")
    
    @property
    def location_string(self):
        if self.city and self.country:
            return f"{self.city}, {self.country}"
        elif self.ip_address:
            return f"IP: {self.ip_address}"
        else:
            return "Location unknown"

class RitoAccount(models.Model):
    name = models.CharField(max_length=100, default="ERROR")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    device = models.OneToOneField(Device, on_delete=models.CASCADE, null=True, blank=True)
    rito_id = models.CharField(max_length=20, unique=True, default=generate_rito_id)
    public_key = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.rito_id

    def generate_custom_rito_id(self):
        """Generate a unique Rito ID in format RITO-XXXXXX"""
        while True:
            random_part = uuid.uuid4().hex[:6].upper()
            rito_id = f"RITO-{random_part}"
            
            if not RitoAccount.objects.filter(rito_id=rito_id).exists():
                return rito_id
    
    def save(self, *args, **kwargs):
        if not self.rito_id:
            self.rito_id = generate_rito_id()
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_rito_account(sender, instance, created, **kwargs):
    """Create RitoAccount when a new User is created"""
    if created:
        # Check if RitoAccount already exists for this user
        if not hasattr(instance, 'ritoaccount'):
            # Generate unique Rito ID first
            while True:
                random_part = uuid.uuid4().hex[:6].upper()
                rito_id = f"RITO-{random_part}"
                
                if not RitoAccount.objects.filter(rito_id=rito_id).exists():
                    break
            
            # Create RitoAccount with generated Rito ID
            RitoAccount.objects.create(
                user=instance, 
                rito_id=rito_id,
                name=instance.username
            )

class SocialMediaAccount(models.Model):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
    ]
    
    rito_account = models.ForeignKey(RitoAccount, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    platform_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['rito_account', 'platform']
    
    def __str__(self):
        return f"{self.platform} - {self.username}"
        
class ContactMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'
    
    def __str__(self):
        return self.email

from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import Count, Q

class CommunityMember(models.Model):
    MEMBERSHIP_CHOICES = [
        ('developer', 'Developer'),
        ('researcher', 'Researcher'),
        ('student', 'Student'),
        ('government', 'Government Official'),
        ('industry', 'Industry Professional'),
        ('citizen', 'Concerned Citizen'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES)
    organization = models.CharField(max_length=255, blank=True)
    interests = models.TextField(help_text="Areas of interest or expertise")
    join_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    bio = models.TextField(blank=True, help_text="Short bio about yourself")
    profile_picture = models.ImageField(upload_to='community/profiles/', blank=True, null=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Social metrics
    reputation_score = models.IntegerField(default=0)
    questions_asked = models.IntegerField(default=0)
    answers_given = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-join_date']
        verbose_name = 'Community Member'
        verbose_name_plural = 'Community Members'
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            name_part = self.name[:3].upper().replace(' ', 'X')
            email_part = self.email.split('@')[0][:3].upper()
            self.user_id = f"AE{name_part}{email_part}{str(uuid.uuid4())[:4].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.user_id})"
    
    def get_absolute_url(self):
        return reverse('user:member_profile', kwargs={'user_id': self.user_id})
    
    @property
    def total_contributions(self):
        return self.questions_asked + self.answers_given

class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    followers = models.ManyToManyField(CommunityMember, related_name='followed_topics', blank=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def questions_count(self):
        return self.questions.filter(is_active=True).count()

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    content = models.TextField(help_text="Detailed description of your question")
    author = models.ForeignKey(CommunityMember, on_delete=models.CASCADE, related_name='questions')
    topics = models.ManyToManyField(Topic, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    
    # Engagement metrics
    views = models.IntegerField(default=0)
    upvotes = models.ManyToManyField(CommunityMember, related_name='upvoted_questions', blank=True)
    downvotes = models.ManyToManyField(CommunityMember, related_name='downvoted_questions', blank=True)
    followers = models.ManyToManyField(CommunityMember, related_name='followed_questions', blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Question.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('user:question_detail', kwargs={'slug': self.slug})
    
    @property
    def vote_count(self):
        return self.upvotes.count() - self.downvotes.count()
    
    @property
    def answers_count(self):
        return self.answers.filter(is_active=True).count()
    
    @property
    def followers_count(self):
        return self.followers.count()

class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    author = models.ForeignKey(CommunityMember, on_delete=models.CASCADE, related_name='answers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    
    # Engagement metrics
    upvotes = models.ManyToManyField(CommunityMember, related_name='upvoted_answers', blank=True)
    downvotes = models.ManyToManyField(CommunityMember, related_name='downvoted_answers', blank=True)
    is_accepted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_accepted', '-created_at']
        unique_together = ['question', 'author']
    
    def __str__(self):
        return f"Answer to {self.question.title}"
    
    @property
    def vote_count(self):
        return self.upvotes.count() - self.downvotes.count()
    
    def accept_answer(self):
        # Unaccept any previously accepted answer for this question
        Answer.objects.filter(question=self.question, is_accepted=True).update(is_accepted=False)
        self.is_accepted = True
        self.save()

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(max_length=1000)
    author = models.ForeignKey(CommunityMember, on_delete=models.CASCADE, related_name='comments')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Engagement
    upvotes = models.ManyToManyField(CommunityMember, related_name='upvoted_comments', blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.name}"

class Space(models.Model):
    """Similar to Quora Spaces - communities within the platform"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    created_by = models.ForeignKey(CommunityMember, on_delete=models.CASCADE, related_name='created_spaces')
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Members and moderators
    members = models.ManyToManyField(CommunityMember, related_name='joined_spaces', blank=True)
    moderators = models.ManyToManyField(CommunityMember, related_name='moderated_spaces', blank=True)
    
    # Space topics
    topics = models.ManyToManyField(Topic, related_name='spaces', blank=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def members_count(self):
        return self.members.count()
    
    @property
    def questions_count(self):
        return self.questions.filter(is_active=True).count()

class SpaceQuestion(models.Model):
    """Questions specifically posted in a Space"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='space_questions')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='questions')
    posted_by = models.ForeignKey(CommunityMember, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['question', 'space']
        ordering = ['-posted_at']

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('answer', 'New Answer'),
        ('comment', 'New Comment'),
        ('upvote', 'Upvote'),
        ('follow', 'New Follower'),
        ('mention', 'Mention'),
        ('space_invite', 'Space Invitation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(CommunityMember, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(CommunityMember, on_delete=models.CASCADE, related_name='acted_notifications')
    verb = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    target_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    target_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    target_space = models.ForeignKey(Space, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.actor.name} {self.get_verb_display()}"

class Bookmark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CommunityMember, on_delete=models.CASCADE, related_name='bookmarks')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'question']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} bookmarked {self.question.title}"

# Signal handlers for updating counts
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Question)
def update_member_question_count(sender, instance, created, **kwargs):
    if created:
        instance.author.questions_asked += 1
        instance.author.save()

@receiver(post_save, sender=Answer)
def update_member_answer_count(sender, instance, created, **kwargs):
    if created:
        instance.author.answers_given += 1
        instance.author.save()

@receiver(post_save, sender=Answer)
@receiver(post_delete, sender=Answer)
def update_question_answer_count(sender, instance, **kwargs):
    # This would be handled by the property, but we can cache it if needed
    pass