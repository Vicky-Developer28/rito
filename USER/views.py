# main/views.py
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# Model imports
from .models import (
    Device, RitoAccount, SocialMediaAccount, ContactMessage, 
    CommunityMember, Subscriber, Question, Answer, Comment, 
    Topic, Space, Notification, Bookmark
)
from .forms import (
    DeviceRegistrationForm, SocialAccountForm, ContactForm, 
    CommunityForm, SubscribeForm, CustomUserCreationForm, 
    CustomAuthenticationForm, QuestionForm, AnswerForm, 
    CommentForm, TopicForm, SpaceForm, CommunityMemberProfileForm
)
from .utils import generate_registration_code, update_device_location, get_client_ip, generate_username

# ========== PROFESSIONAL SUPERUSER DECORATOR ==========

def superuser_required(function=None, redirect_field_name=None, login_url=None):
    """
    Professional decorator for views that require superuser access.
    """
    if login_url is None:
        login_url = settings.LOGIN_URL
    
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator


def sorry(request):
    return render(request, 'develop.html')
# ========== PUBLIC VIEWS ==========

def index(request):
    """Home page"""
    return render(request, 'index.html')

def community_join(request):
    """Community join page with popular and recent questions"""
    
    # Get popular questions (ordered by vote count and answer count)
    popular_questions = Question.objects.filter(is_active=True).order_by('-views', '-created_at')[:5]
    
    # Get recent questions
    recent_questions = Question.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    # Prefetch related data to optimize queries
    popular_questions = popular_questions.prefetch_related('topics', 'answers', 'upvotes', 'downvotes')
    recent_questions = recent_questions.prefetch_related('topics', 'answers', 'upvotes', 'downvotes')
    
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            try:
                member = form.save()
                send_mail(
                    'Welcome to Aegis Innovative Community',
                    f'Hello {member.name},\n\nThank you for joining the Aegis Innovative community! '
                    f'Your user ID is: {member.user_id}\n\nWe will keep you updated on our progress '
                    f'and upcoming events.\n\nBest regards,\nAegis Innovative Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [member.email],
                    fail_silently=True,
                )
                messages.success(request, 
                    f'Welcome to the community, {member.name}! Your user ID is: {member.user_id}')
                return redirect('main:community_join')
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CommunityForm()
    
    context = {
        'form': form,
        'popular_questions': popular_questions,
        'recent_questions': recent_questions,
    }
    
    return render(request, 'community/community_join.html', context)

def docs(request):
    try:
        """Documentation page"""
        return render(request, 'docs.html')
    except:
        return render(request, 'develop.html')
def faq(request):
    try:
        """FAQ page"""
        faqs = [
            {
                'question': 'What makes Project Rito different from existing digital identity solutions?',
                'answer': 'Project Rito establishes a hardware-rooted chain of trust, sovereign OS layers, '
                        'and integrates identity at the protocol level rather than just application level.'
            },
            {
                'question': 'How does the device registration work?',
                'answer': 'Each device gets a unique IEDA (Identity Encryption Device Address) that forms the root of trust for your digital identity.'
            },
            {
                'question': 'Is my data secure?',
                'answer': 'Yes, we use end-to-end encryption and decentralized storage to ensure your data remains private and secure.'
            }
        ]
        return render(request, 'faq.html', {'faqs': faqs})
    except:
        return render(request, 'develop.html')

def contact(request):
    """Contact form page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            email_content = f"""
            New Contact Form Submission:
            
            Name: {contact_message.name}
            Email: {contact_message.email}
            Subject: {contact_message.subject}
            
            Message:
            {contact_message.message}
            
            Received: {contact_message.created_at}
            """
            
            try:
                send_mail(
                    f'Contact Form: {contact_message.subject}',
                    email_content,
                    settings.DEFAULT_FROM_EMAIL,
                    ['vicky28.developer@gmail.com', 'aegisinitiative45@gmail.com'],
                    fail_silently=True,
                )
                messages.success(request, 
                    'Thank you for your message! We will get back to you soon.')
                return redirect('main:contact')
            except Exception as e:
                messages.error(request, 
                    'Your message was saved, but there was an error sending the email notification.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def subscribe(request):
    """Newsletter subscription"""
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            try:
                subscriber = form.save()
                send_mail(
                    'Welcome to Aegis Innovative Newsletter',
                    'Thank you for subscribing to our newsletter! '
                    'You will receive updates about Project Rito and our initiatives.',
                    settings.DEFAULT_FROM_EMAIL,
                    [subscriber.email],
                    fail_silently=True,
                )
                messages.success(request, 
                    'Thank you for subscribing to our newsletter!')
            except:
                messages.error(request, 
                    'This email is already subscribed to our newsletter.')
        else:
            messages.error(request, 'Please enter a valid email address.')
    
    return redirect('main:index')

# ========== AUTHENTICATION VIEWS ==========

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Project Rito.')
            return redirect('main:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    """
    Professional login view with proper authentication handling
    """
    # If user is already authenticated, redirect appropriately
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('main:dashboard')
        else:
            messages.info(request, 'You are already logged in.')
            return redirect('main:index')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Handle next parameter safely
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and next_url != '/':
                    return redirect(next_url)
                else:
                    if user.is_superuser:
                        return redirect('main:dashboard')
                    else:
                        return redirect('main:index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomAuthenticationForm()
        # Preserve next parameter in GET requests
        next_url = request.GET.get('next')
        if next_url:
            form.initial['next'] = next_url
    
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    """Logs out the current user"""
    auth_logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('main:login')

# ========== DEVICE REGISTRATION & MANAGEMENT ==========

@login_required
def dashboard(request):
    """
    Professional dashboard view with device location tracking
    """
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('main:index')
    
    try:
        rito_account = RitoAccount.objects.filter(user=request.user).first()
        social_accounts = SocialMediaAccount.objects.filter(rito_account=rito_account) if rito_account else []
        device = rito_account.device if rito_account else None
        
        # Prepare location data for template
        location_data = None
        if device:
            # Update device location on each dashboard load
            ip_address = get_client_ip(request)
            update_device_location(device, ip_address)
            
            if device.latitude and device.longitude:
                location_data = {
                    'lat': device.latitude,
                    'lng': device.longitude,
                    'city': device.city,
                    'country': device.country,
                    'ip': device.ip_address,
                    'last_seen': device.last_seen,
                    'location_string': device.location_string
                }
        
        context = {
            'account': rito_account,
            'social_accounts': social_accounts,
            'device': device,
            'location_data': location_data,
            'user': request.user
        }
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return render(request, 'dashboard.html', {'user': request.user})

@login_required
def register_device_view(request):
    """Device registration view with 6-digit code verification"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('main:index')
    
    if request.method == 'POST':
        form = DeviceRegistrationForm(request.POST)
        if form.is_valid():
            ieda = form.cleaned_data['ieda']
            code = form.cleaned_data['code']
            
            try:
                # Check if device already exists
                if Device.objects.filter(ieda=ieda).exists():
                    messages.error(request, 'Device already registered')
                    return render(request, 'register.html', {'form': form})
                
                # Verify the registration code
                if len(code) != 6 or not code.isdigit():
                    messages.error(request, 'Invalid registration code format')
                    return render(request, 'register.html', {'form': form})
                
                # Create device with the provided code
                device = Device.objects.create(
                    ieda=ieda,
                    mac_address=f"MAC_{ieda[:8]}",
                    registration_code=code
                )
                
                # Update device location
                ip_address = get_client_ip(request)
                update_device_location(device, ip_address)
                
                # Create or update Rito account linked to user
                rito_account, created = RitoAccount.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'device': device,
                        'name': f"{request.user.username}'s Account"
                    }
                )
                
                if not created:
                    rito_account.device = device
                    rito_account.save()
                
                messages.success(request, f'Device registered successfully! Your Rito ID: {rito_account.rito_id}')
                return redirect('main:dashboard')
                
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                return render(request, 'register.html', {'form': form})
    else:
        form = DeviceRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def create_social_account(request):
    """Create social media account"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('main:index')
    
    if request.method == 'POST':
        form = SocialAccountForm(request.POST)
        if form.is_valid():
            platform = form.cleaned_data['platform']
            
            try:
                rito_account = get_object_or_404(RitoAccount, user=request.user)
                
                # Check if platform account already exists
                if SocialMediaAccount.objects.filter(rito_account=rito_account, platform=platform).exists():
                    messages.warning(request, f'{platform.capitalize()} account already exists')
                    return redirect('main:dashboard')
                
                # Generate username and platform ID
                username = generate_username(platform, rito_account.rito_id)
                platform_id = f"{platform}_{uuid.uuid4().hex[:8]}"
                
                # Create social media account
                social_account = SocialMediaAccount.objects.create(
                    rito_account=rito_account,
                    platform=platform,
                    platform_id=platform_id,
                    username=username
                )
                
                messages.success(request, f'{platform.capitalize()} account created successfully!')
                return redirect('main:dashboard')
                
            except RitoAccount.DoesNotExist:
                messages.error(request, 'Please register a device first')
                return redirect('main:register_device')
            except Exception as e:
                messages.error(request, f'Failed to create account: {str(e)}')
                return redirect('main:dashboard')
    else:
        form = SocialAccountForm()
    
    return render(request, 'create_social_account.html', {'form': form})

@login_required
def account_detail(request, platform):
    """Social account detail view"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('main:index')
    
    try:
        rito_account = get_object_or_404(RitoAccount, user=request.user)
        social_account = get_object_or_404(
            SocialMediaAccount, 
            rito_account=rito_account, 
            platform=platform
        )
        
        context = {
            'account': rito_account,
            'social_account': social_account
        }
        return render(request, 'account_detail.html', context)
        
    except SocialMediaAccount.DoesNotExist:
        raise Http404("Social account not found")

@login_required
def delete_social_account(request, platform):
    """Delete social media account"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser privileges required.')
        return redirect('main:index')
    
    if request.method == 'POST':
        try:
            rito_account = get_object_or_404(RitoAccount, user=request.user)
            social_account = get_object_or_404(
                SocialMediaAccount, 
                rito_account=rito_account, 
                platform=platform
            )
            
            platform_name = social_account.get_platform_display()
            social_account.delete()
            
            messages.success(request, f'{platform_name} account deleted successfully')
            return redirect('main:dashboard')
            
        except SocialMediaAccount.DoesNotExist:
            messages.error(request, 'Account not found')
    
    return redirect('main:dashboard')

# ========== API ENDPOINTS ==========

@csrf_exempt
def device_register_api(request):
    """API endpoint for ESP8266 device registration and code generation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ieda = data.get('ieda')
            mac_address = data.get('mac_address')
            requested_user = data.get('requested_user')
            
            if not ieda:
                return JsonResponse({
                    'status': 'error',
                    'message': 'IEDA is required'
                }, status=400)
            
            # Generate a new 6-digit registration code
            registration_code = generate_registration_code()
            
            # Check if device already exists
            device, created = Device.objects.get_or_create(
                ieda=ieda,
                defaults={
                    'mac_address': mac_address or f"MAC_{ieda[:8]}",
                    'registration_code': registration_code,
                    'is_active': False
                }
            )
            
            if not created:
                # Update existing device with new code
                device.registration_code = registration_code
                device.is_active = False
                device.save()
            
            response_data = {
                'status': 'success',
                'registration_code': registration_code,
                'device_exists': not created,
                'message': 'Registration code generated successfully'
            }
            
            # Add user information to response if provided
            if requested_user:
                response_data['requested_user'] = requested_user
                response_data['message'] = f'Registration code generated for user {requested_user}'
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def device_status_api(request):
    """API endpoint for device status check with user verification"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ieda = data.get('ieda')
            username = data.get('username')
            
            if not ieda:
                return JsonResponse({
                    'status': 'error',
                    'message': 'IEDA is required'
                }, status=400)
            
            try:
                device = Device.objects.get(ieda=ieda)
                rito_account = RitoAccount.objects.filter(device=device).first()
                
                # Check if device is registered to the specific user
                registered_to_user = False
                user_rito_id = None
                
                if rito_account and username:
                    # Verify if the device is registered to the requested user
                    registered_to_user = (rito_account.user.username == username)
                    user_rito_id = rito_account.rito_id
                
                # Update last seen timestamp
                device.last_seen = timezone.now()
                device.save()
                
                response_data = {
                    'status': 'success',
                    'registered': rito_account is not None,
                    'registered_to_user': registered_to_user,
                    'rito_id': user_rito_id,
                    'registration_code': device.registration_code,
                    'is_active': device.is_active,
                    'last_seen': device.last_seen.isoformat()
                }
                
                # Add username info if available
                if rito_account and rito_account.user:
                    response_data['username'] = rito_account.user.username
                
                # Add custom message based on registration status
                if registered_to_user:
                    response_data['message'] = f'Device registered to user {username}'
                elif rito_account and not registered_to_user:
                    actual_user = rito_account.user.username
                    response_data['message'] = f'Device registered to different user: {actual_user}'
                else:
                    response_data['message'] = 'Device not registered'
                
                return JsonResponse(response_data)
                
            except Device.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Device not found'
                }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def device_location_api(request):
    """API endpoint to update device location with user info"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ieda = data.get('ieda')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            ip_address = data.get('ip_address')
            username = data.get('username')
            
            if not ieda:
                return JsonResponse({
                    'status': 'error',
                    'message': 'IEDA is required'
                }, status=400)
            
            try:
                device = Device.objects.get(ieda=ieda)
                
                # Update location data
                if latitude and longitude:
                    device.latitude = float(latitude)
                    device.longitude = float(longitude)
                
                if ip_address:
                    device.ip_address = ip_address
                    update_device_location(device, ip_address)
                
                device.last_seen = timezone.now()
                device.save()
                
                response_data = {
                    'status': 'success',
                    'message': 'Location updated successfully',
                }
                
                # Add user info to response
                if username:
                    response_data['user'] = username
                
                # Include location details if available
                if device.latitude and device.longitude:
                    response_data['location'] = {
                        'latitude': device.latitude,
                        'longitude': device.longitude,
                        'city': device.city,
                        'country': device.country
                    }
                
                return JsonResponse(response_data)
                
            except Device.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Device not found'
                }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@login_required
@csrf_exempt
def refresh_registration_code(request):
    """API endpoint to refresh registration code"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ieda = data.get('ieda')
            
            if not ieda:
                return JsonResponse({
                    'status': 'error',
                    'message': 'IEDA is required'
                }, status=400)
            
            try:
                device = Device.objects.get(ieda=ieda)
                new_code = generate_registration_code()
                device.registration_code = new_code
                device.save()
                
                return JsonResponse({
                    'status': 'success',
                    'registration_code': new_code,
                    'message': 'Registration code refreshed successfully'
                })
                
            except Device.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Device not found'
                }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

# ========== COMMUNITY VIEWS (Quora-like) ==========

@login_required
def community_home(request):
    """Community home page - Quora-like feed"""
    try:
        # Get community member profile
        try:
            member = CommunityMember.objects.get(email=request.user.email)
        except CommunityMember.DoesNotExist:
            member = None
            messages.info(request, 'Complete your community profile to participate fully!')
        
        # Get questions with pagination
        questions_list = Question.objects.filter(is_active=True).select_related('author').prefetch_related('topics').order_by('-created_at')
        paginator = Paginator(questions_list, 10)
        page = request.GET.get('page')
        questions = paginator.get_page(page)
        
        # Get trending topics
        trending_topics = Topic.objects.filter(is_active=True).annotate(
            question_count=Count('questions')
        ).order_by('-question_count')[:10]
        
        # Get member count
        member_count = CommunityMember.objects.filter(is_active=True).count()
        
        context = {
            'member': member,
            'questions': questions,
            'trending_topics': trending_topics,
            'member_count': member_count,
        }
        return render(request, 'community/home.html', context)
        
    except Exception as e:
        messages.error(request, 'Error loading community')
        return render(request, 'community/home.html')

@login_required
def ask_question(request):
    """Ask a new question"""
    # Check if user has a CommunityMember profile
    try:
        member = CommunityMember.objects.get(email=request.user.email)
    except CommunityMember.DoesNotExist:
        messages.error(request, 'You need to create a community profile first!')
        return redirect('main:community_join')
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = member
            question.save()
            form.save_m2m()  # Save many-to-many relationships (topics)
            
            messages.success(request, 'Your question has been posted!')
            return redirect('main:question_detail', slug=question.slug)
    else:
        form = QuestionForm()
    
    return render(request, 'community/ask_question.html', {'form': form})

@login_required
def question_detail(request, slug):
    """Question detail page with answers"""
    question = get_object_or_404(Question, slug=slug, is_active=True)
    answers = question.answers.filter(is_active=True).select_related('author')
    
    # Check if user has a CommunityMember profile
    try:
        member = CommunityMember.objects.get(email=request.user.email)
        is_bookmarked = Bookmark.objects.filter(user=member, question=question).exists()
    except CommunityMember.DoesNotExist:
        member = None
        is_bookmarked = False
    
    # Increment view count
    question.views += 1
    question.save()
    
    # Answer form
    answer_form = AnswerForm()
    
    context = {
        'question': question,
        'answers': answers,
        'member': member,
        'answer_form': answer_form,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'community/question_detail.html', context)

@login_required
def post_answer(request, slug):
    """Post an answer to a question"""
    # Check if user has a CommunityMember profile
    try:
        member = CommunityMember.objects.get(email=request.user.email)
    except CommunityMember.DoesNotExist:
        messages.error(request, 'You need to create a community profile first!')
        return redirect('main:community_join')
    
    if request.method == 'POST':
        question = get_object_or_404(Question, slug=slug, is_active=True)
        
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = member
            answer.save()
            
            messages.success(request, 'Your answer has been posted!')
        else:
            messages.error(request, 'Please correct the errors in your answer.')
    
    return redirect('main:question_detail', slug=slug)

@login_required
def vote_question(request, slug, vote_type):
    """Upvote or downvote a question"""
    # Check if user has a CommunityMember profile
    try:
        member = CommunityMember.objects.get(email=request.user.email)
    except CommunityMember.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Community profile required'})
    
    if request.method == 'POST':
        question = get_object_or_404(Question, slug=slug, is_active=True)
        
        if vote_type == 'upvote':
            if question.downvotes.filter(id=member.id).exists():
                question.downvotes.remove(member)
            question.upvotes.add(member)
        elif vote_type == 'downvote':
            if question.upvotes.filter(id=member.id).exists():
                question.upvotes.remove(member)
            question.downvotes.add(member)
        elif vote_type == 'remove':
            question.upvotes.remove(member)
            question.downvotes.remove(member)
        
        return JsonResponse({
            'success': True,
            'vote_count': question.vote_count,
            'upvotes': question.upvotes.count(),
            'downvotes': question.downvotes.count()
        })
    
    return JsonResponse({'success': False})

@login_required
def follow_question(request, slug):
    """Follow/unfollow a question"""
    # Check if user has a CommunityMember profile
    try:
        member = CommunityMember.objects.get(email=request.user.email)
    except CommunityMember.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Community profile required'})
    
    if request.method == 'POST':
        question = get_object_or_404(Question, slug=slug, is_active=True)
        
        if question.followers.filter(id=member.id).exists():
            question.followers.remove(member)
            followed = False
        else:
            question.followers.add(member)
            followed = True
        
        return JsonResponse({
            'success': True,
            'followed': followed,
            'followers_count': question.followers_count
        })
    
    return JsonResponse({'success': False})

@login_required
def bookmark_question(request, slug):
    """Bookmark/unbookmark a question"""
    # Check if user has a CommunityMember profile
    try:
        member = CommunityMember.objects.get(email=request.user.email)
    except CommunityMember.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Community profile required'})
    
    if request.method == 'POST':
        question = get_object_or_404(Question, slug=slug, is_active=True)
        
        bookmark, created = Bookmark.objects.get_or_create(
            user=member,
            question=question
        )
        
        if not created:
            bookmark.delete()
            bookmarked = False
        else:
            bookmarked = True
        
        return JsonResponse({
            'success': True,
            'bookmarked': bookmarked
        })
    
    return JsonResponse({'success': False})

@login_required
def accept_answer(request, answer_id):
    """Accept an answer as the solution"""
    # Check if user has a CommunityMember profile
    try:
        member = CommunityMember.objects.get(email=request.user.email)
    except CommunityMember.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Community profile required'})
    
    if request.method == 'POST':
        answer = get_object_or_404(Answer, id=answer_id, is_active=True)
        
        # Check if the member is the question author
        if answer.question.author == member:
            answer.accept_answer()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def member_profile(request, user_id):
    """Community member profile - public view"""
    member = get_object_or_404(CommunityMember, user_id=user_id, is_active=True)
    questions = member.questions.filter(is_active=True).order_by('-created_at')[:10]
    answers = member.answers.filter(is_active=True).order_by('-created_at')[:10]
    
    context = {
        'profile_member': member,
        'questions': questions,
        'answers': answers,
    }
    return render(request, 'community/member_profile.html', context)

@login_required
def topics(request):
    """Browse all topics"""
    topics_list = Topic.objects.filter(is_active=True).annotate(
        question_count=Count('questions')
    ).order_by('name')
    
    context = {
        'topics': topics_list,
    }
    return render(request, 'community/topics.html', context)

@login_required
def topic_detail(request, slug):
    """Topic detail page with related questions"""
    topic = get_object_or_404(Topic, slug=slug, is_active=True)
    questions = topic.questions.filter(is_active=True).order_by('-created_at')
    
    # Check if member follows this topic
    try:
        member = CommunityMember.objects.get(email=request.user.email)
        is_following = topic.followers.filter(id=member.id).exists()
    except CommunityMember.DoesNotExist:
        member = None
        is_following = False
    
    context = {
        'topic': topic,
        'questions': questions,
        'is_following': is_following,
    }
    return render(request, 'community/topic_detail.html', context)

@login_required
def follow_topic(request, slug):
    """Follow/unfollow a topic"""
    # Check if user has a CommunityMember profile
    try:
        member = CommunityMember.objects.get(email=request.user.email)
    except CommunityMember.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Community profile required'})
    
    if request.method == 'POST':
        topic = get_object_or_404(Topic, slug=slug, is_active=True)
        
        if topic.followers.filter(id=member.id).exists():
            topic.followers.remove(member)
            following = False
        else:
            topic.followers.add(member)
            following = True
        
        return JsonResponse({
            'success': True,
            'following': following,
            'followers_count': topic.followers_count
        })
    
    return JsonResponse({'success': False})

@login_required
def search(request):
    """Search questions and answers"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = Question.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_active=True
        ).select_related('author').prefetch_related('topics')
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'community/search.html', context)