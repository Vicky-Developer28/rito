import os
from pathlib import Path
from django.urls import reverse_lazy
# Add these imports at the top of settings.py
from django.template import Library
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q


# Create template register (if keeping filters in settings)
register = Library()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-mhh9u#6i#-iob%*6j-gw3brv^je@g1gc)^1hlfg^+psyf_wqo0')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ADMINS = [("Admin", "vicky28.developer@gmail.com")]

ALLOWED_HOSTS = [
    't67tfr22-8000.inc1.devtunnels.ms',  # Remove https:// and trailing slash
    'localhost',                          # Fixed typo
    '127.0.0.1',
]
# Application definition
INSTALLED_APPS = [
    # Unfold Admin Theme (must be first)
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    
    # Django Core Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party Apps
    'rest_framework',
    'rest_framework.authtoken',
    'ninja',
    'import_export',

    # Local Apps
    'USER.apps.UserConfig',
]

# Portal/settings.py
APPEND_SLASH = False

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'Portal.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Portal.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Custom date/time input formats
DATETIME_INPUT_FORMATS = ["%d-%m-%Y %H:%M:%S"]
DATE_INPUT_FORMATS = ["%d %b, %Y"]

# Email Settings
DEFAULT_FROM_EMAIL = 'Aegis Innovative <noreply@aegisinnovative.com>'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 903694689  # ~861 MB

# Static and Media Files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Settings (for Production)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Authentication settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Password reset
PASSWORD_RESET_TIMEOUT = 4017

# Custom encryption key
ENCRYPT_KEY = os.environ.get('RITO_ENCRYPT_KEY', 'a-default-insecure-key-for-dev-only')

# ========== UNFOLD ADMIN THEME CONFIGURATION ==========

UNFOLD = {
    # ========== BASIC CONFIGURATION ==========
    "SITE_TITLE": "Aegis Innovative - Sovereign Digital Identity",
    "SITE_HEADER": "Aegis Admin Portal",
    "SITE_URL": "/",
    "SITE_SYMBOL": "fingerprint",  # Changed to fingerprint for identity theme
    "SITE_FAVICON": "/static/svg/Aegis-Ligth.svg",
    "SITE_LOGO": {
        "light": "/static/svg/Aegis-Dark.svg",
        "dark": "/static/svg/Aegis-Ligth.svg",
    },
    "SITE_ICON": {
        "light": "/static/svg/Aegis-Dark.svg",
        "dark": "/static/svg/Aegis-Ligth.svg",
    },
    
    # ========== THEME & APPEARANCE ==========
    "THEME": "dark",
    "DARK_MODE_SUPPORT": True,
    "THEME_COLOR": "blue",
    "BACKGROUND_COLOR": "slate",
    
    # ========== ADVANCED COLOR SCHEMES ==========
    "COLORS": {
        "primary": {
            "50": "238, 242, 255",
            "100": "224, 231, 255", 
            "200": "199, 210, 254",
            "300": "165, 180, 252",
            "400": "129, 140, 248",
            "500": "99, 102, 241",   # Primary brand blue
            "600": "79, 70, 229",
            "700": "67, 56, 202",
            "800": "55, 48, 163",
            "900": "49, 46, 129",
            "950": "30, 27, 75",
        },
        "secondary": {
            "50": "240, 253, 250",
            "100": "204, 251, 241",
            "200": "153, 246, 228",
            "300": "94, 234, 212",
            "400": "45, 212, 191",
            "500": "20, 184, 166",   # Teal accent
            "600": "13, 148, 136",
            "700": "15, 118, 110",
            "800": "17, 94, 89",
            "900": "19, 78, 74",
            "950": "4, 47, 46",
        },
        "accent": {
            "50": "253, 242, 248",
            "100": "252, 231, 243",
            "200": "251, 207, 232",
            "300": "249, 168, 212",
            "400": "244, 114, 182",
            "500": "236, 72, 153",   # Pink accent
            "600": "219, 39, 119",
            "700": "190, 24, 93",
            "800": "157, 23, 77",
            "900": "131, 24, 67",
            "950": "80, 7, 36",
        },
        "success": {
            "50": "240, 253, 244",
            "100": "220, 252, 231",
            "200": "187, 247, 208",
            "300": "134, 239, 172",
            "400": "74, 222, 128",
            "500": "34, 197, 94",    # Green success
            "600": "22, 163, 74",
            "700": "21, 128, 61",
            "800": "22, 101, 52",
            "900": "20, 83, 45",
            "950": "5, 46, 22",
        },
        "warning": {
            "50": "255, 251, 235",
            "100": "254, 243, 199",
            "200": "253, 230, 138",
            "300": "252, 211, 77",
            "400": "251, 191, 36",
            "500": "245, 158, 11",   # Amber warning
            "600": "217, 119, 6",
            "700": "180, 83, 9",
            "800": "146, 64, 14",
            "900": "120, 53, 15",
            "950": "69, 26, 3",
        },
        "error": {
            "50": "254, 242, 242",
            "100": "254, 226, 226",
            "200": "254, 202, 202",
            "300": "252, 165, 165",
            "400": "248, 113, 113",
            "500": "239, 68, 68",    # Red error
            "600": "220, 38, 38",
            "700": "185, 28, 28",
            "800": "153, 27, 27",
            "900": "127, 29, 29",
            "950": "69, 10, 10",
        },
        "gray": {
            "50": "249, 250, 251",
            "100": "243, 244, 246",
            "200": "229, 231, 235",
            "300": "209, 213, 219",
            "400": "156, 163, 175",
            "500": "107, 114, 128",
            "600": "75, 85, 99",
            "700": "55, 65, 81",
            "800": "31, 41, 55",
            "900": "17, 24, 39",
            "950": "3, 7, 18",
        },
        "slate": {
            "50": "248, 250, 252",
            "100": "241, 245, 249",
            "200": "226, 232, 240",
            "300": "203, 213, 225",
            "400": "148, 163, 184",
            "500": "100, 116, 139",
            "600": "71, 85, 105",
            "700": "51, 65, 85",
            "800": "30, 41, 59",
            "900": "15, 23, 42",
            "950": "2, 6, 23",
        }
    },
    
    # ========== TYPOGRAPHY & FONTS ==========
    "TYPOGRAPHY": {
        "font_family": {
            "primary": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            "mono": "'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, 'Cascadia Code', monospace",
        },
        "font_sizes": {
            "xs": "0.75rem",
            "sm": "0.875rem",
            "base": "1rem",
            "lg": "1.125rem",
            "xl": "1.25rem",
            "2xl": "1.5rem",
            "3xl": "1.875rem",
            "4xl": "2.25rem",
            "5xl": "3rem",
        },
        "font_weights": {
            "light": "300",
            "normal": "400",
            "medium": "500",
            "semibold": "600",
            "bold": "700",
            "extrabold": "800",
        },
        "line_heights": {
            "tight": "1.25",
            "normal": "1.5",
            "relaxed": "1.75",
        },
    },
    
    # ========== LAYOUT & SPACING ==========
    "SPACING": {
        "xs": "0.25rem",
        "sm": "0.5rem",
        "md": "1rem",
        "lg": "1.5rem",
        "xl": "2rem",
        "2xl": "3rem",
        "3xl": "4rem",
    },
    "BORDER_RADIUS": {
        "none": "0",
        "sm": "0.125rem",
        "default": "0.25rem",
        "md": "0.375rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "2xl": "1rem",
        "full": "9999px",
    },
    "SHADOWS": {
        "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
        "default": "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
        "md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
        "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
        "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
        "2xl": "0 25px 50px -12px rgb(0 0 0 / 0.25)",
    },
    
    # ========== SIDEBAR CONFIGURATION ==========
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "collapse_after": 10,
        "navigation_style": "accordion",
        "width": {
            "collapsed": "4rem",
            "expanded": "16rem",
        },
        "background": "slate-900",
        "text_color": "slate-200",
        "hover_background": "slate-800",
        "active_background": "blue-600",
        "active_text_color": "white",
        "border_color": "slate-700",
        "scrollbar": {
            "track": "slate-700",
            "thumb": "slate-500",
            "thumb_hover": "slate-400",
        },
    },
    
    # ========== ADVANCED NAVIGATION ==========
    "NAVIGATION": [
        {
            "title": "Dashboard & Analytics",
            "separator": True,
            "icon": "dashboard",
            "badge": "new",
            "items": [
                {
                    "title": "System Overview",
                    "icon": "insights",
                    "link": reverse_lazy("admin:index"),
                    "badge": "pro",
                    "description": "Real-time system metrics and health monitoring",
                },
                {
                    "title": "Performance Analytics",
                    "icon": "analytics",
                    "link": reverse_lazy("admin:performance_dashboard"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "Security Dashboard",
                    "icon": "security",
                    "link": reverse_lazy("admin:security_dashboard"),
                    "permission": lambda request: request.user.is_superuser,
                },
            ],
        },
        {
            "title": "Identity Management",
            "separator": True,
            "icon": "fingerprint",
            "items": [
                {
                    "title": "Digital Identities",
                    "icon": "badge",
                    "link": reverse_lazy("admin:main_ritoaccount_changelist"),
                    "badge": lambda: RitoAccount.objects.count(),
                    "badge_color": "blue",
                },
                {
                    "title": "Identity Verification",
                    "icon": "verified_user",
                    "link": reverse_lazy("admin:identity_verification"),
                    "permission": lambda request: request.user.has_perm('main.verify_identity'),
                },
                {
                    "title": "Biometric Data",
                    "icon": "fingerprint",
                    "link": reverse_lazy("admin:biometric_data"),
                    "permission": lambda request: request.user.is_superuser,
                },
            ],
        },
        {
            "title": "Device Ecosystem",
            "separator": True,
            "icon": "devices",
            "items": [
                {
                    "title": "Registered Devices",
                    "icon": "phone_iphone",
                    "link": reverse_lazy("admin:main_device_changelist"),
                    "badge": lambda: Device.objects.filter(is_active=True).count(),
                    "badge_color": "green",
                },
                {
                    "title": "Device Health",
                    "icon": "monitor_heart",
                    "link": reverse_lazy("admin:device_health"),
                    "description": "Device connectivity and performance metrics",
                },
                {
                    "title": "Firmware Management",
                    "icon": "system_update",
                    "link": reverse_lazy("admin:firmware_management"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "Security Certificates",
                    "icon": "certificate",
                    "link": reverse_lazy("admin:certificate_management"),
                    "permission": lambda request: request.user.is_superuser,
                },
            ],
        },
        {
            "title": "Social Integration",
            "separator": True,
            "icon": "share",
            "items": [
                {
                    "title": "Social Accounts",
                    "icon": "account_circle",
                    "link": reverse_lazy("admin:main_socialmediaaccount_changelist"),
                    "badge": lambda: SocialMediaAccount.objects.count(),
                },
                {
                    "title": "Platform Analytics",
                    "icon": "trending_up",
                    "link": reverse_lazy("admin:social_analytics"),
                },
                {
                    "title": "Integration Settings",
                    "icon": "settings",
                    "link": reverse_lazy("admin:integration_settings"),
                },
            ],
        },
        {
            "title": "Community Platform",
            "separator": True,
            "icon": "groups",
            "items": [
                {
                    "title": "Community Members",
                    "icon": "people",
                    "link": reverse_lazy("admin:main_communitymember_changelist"),
                    "badge": lambda: CommunityMember.objects.filter(is_active=True).count(),
                    "badge_color": "purple",
                },
                {
                    "title": "Knowledge Base",
                    "icon": "library_books",
                    "link": reverse_lazy("admin:main_question_changelist"),
                    "badge": lambda: Question.objects.filter(is_active=True).count(),
                },
                {
                    "title": "Expert Answers",
                    "icon": "question_answer",
                    "link": reverse_lazy("admin:main_answer_changelist"),
                    "badge": lambda: Answer.objects.filter(is_active=True).count(),
                },
                {
                    "title": "Discussion Spaces",
                    "icon": "forum",
                    "link": reverse_lazy("admin:main_space_changelist"),
                    "badge": lambda: Space.objects.filter(is_active=True).count(),
                },
                {
                    "title": "Content Moderation",
                    "icon": "moderator",
                    "link": reverse_lazy("admin:content_moderation"),
                    "permission": lambda request: request.user.has_perm('main.moderate_content'),
                },
                {
                    "title": "Community Analytics",
                    "icon": "analytics",
                    "link": reverse_lazy("admin:community_analytics"),
                },
            ],
        },
        {
            "title": "Communication Hub",
            "separator": True,
            "icon": "chat",
            "items": [
                {
                    "title": "Contact Messages",
                    "icon": "contact_mail",
                    "link": reverse_lazy("admin:main_contactmessage_changelist"),
                    "badge": lambda: ContactMessage.objects.filter(is_read=False).count(),
                    "badge_color": "red",
                },
                {
                    "title": "Newsletter Subscribers",
                    "icon": "subscriptions",
                    "link": reverse_lazy("admin:main_subscriber_changelist"),
                    "badge": lambda: Subscriber.objects.filter(is_active=True).count(),
                    "badge_color": "green",
                },
                {
                    "title": "Notification Center",
                    "icon": "notifications",
                    "link": reverse_lazy("admin:main_notification_changelist"),
                },
                {
                    "title": "Email Campaigns",
                    "icon": "email",
                    "link": reverse_lazy("admin:email_campaigns"),
                    "permission": lambda request: request.user.is_superuser,
                },
            ],
        },
        {
            "title": "User Engagement",
            "separator": True,
            "icon": "engagement",
            "items": [
                {
                    "title": "User Bookmarks",
                    "icon": "bookmark",
                    "link": reverse_lazy("admin:main_bookmark_changelist"),
                },
                {
                    "title": "Voting Analytics",
                    "icon": "thumbs_up_down",
                    "link": reverse_lazy("admin:voting_analytics"),
                },
                {
                    "title": "User Behavior",
                    "icon": "psychology",
                    "link": reverse_lazy("admin:user_behavior"),
                    "permission": lambda request: request.user.is_superuser,
                },
            ],
        },
        {
            "title": "System Administration",
            "separator": True,
            "icon": "admin_panel_settings",
            "items": [
                {
                    "title": "User Management",
                    "icon": "manage_accounts",
                    "link": reverse_lazy("admin:auth_user_changelist"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "Group Permissions",
                    "icon": "groups",
                    "link": reverse_lazy("admin:auth_group_changelist"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "System Logs",
                    "icon": "list_alt",
                    "link": reverse_lazy("admin:system_logs"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "Backup & Restore",
                    "icon": "backup",
                    "link": reverse_lazy("admin:backup_restore"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "API Management",
                    "icon": "api",
                    "link": reverse_lazy("admin:api_management"),
                    "permission": lambda request: request.user.is_superuser,
                },
            ],
        },
        {
            "title": "Security & Compliance",
            "separator": True,
            "icon": "security",
            "items": [
                {
                    "title": "Audit Trail",
                    "icon": "history",
                    "link": reverse_lazy("admin:audit_trail"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "Security Policies",
                    "icon": "policy",
                    "link": reverse_lazy("admin:security_policies"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "Compliance Reports",
                    "icon": "assignment",
                    "link": reverse_lazy("admin:compliance_reports"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "Data Encryption",
                    "icon": "encryption",
                    "link": reverse_lazy("admin:encryption_settings"),
                    "permission": lambda request: request.user.is_superuser,
                },
            ],
        },
        {
            "title": "Advanced Features",
            "separator": True,
            "icon": "tune",
            "items": [
                {
                    "title": "AI Assistant",
                    "icon": "smart_toy",
                    "link": reverse_lazy("admin:ai_assistant"),
                    "badge": "AI",
                    "badge_color": "purple",
                },
                {
                    "title": "Workflow Automation",
                    "icon": "auto_awesome",
                    "link": reverse_lazy("admin:workflow_automation"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": "Custom Reports",
                    "icon": "assessment",
                    "link": reverse_lazy("admin:custom_reports"),
                },
                {
                    "title": "Data Export",
                    "icon": "download",
                    "link": reverse_lazy("admin:data_export"),
                },
            ],
        },
    ],
    
    # ========== HEADER CONFIGURATION ==========
    "HEADER": {
        "height": "4rem",
        "background": "slate-900",
        "text_color": "white",
        "show_breadcrumbs": True,
        "show_user_profile": True,
        "show_notifications": True,
        "show_search": True,
        "notification_badge_color": "red",
        "user_menu": {
            "show_profile": True,
            "show_settings": True,
            "show_logout": True,
            "show_theme_switcher": True,
        },
    },
    
    # ========== DASHBOARD CUSTOMIZATION ==========
    "DASHBOARD_CALLBACK": "Portal.settings.advanced_dashboard_callback",
    "DASHBOARD": {
        "show_quick_actions": True,
        "show_recent_activity": True,
        "show_system_stats": True,
        "show_charts": True,
        "show_notifications": True,
        "layout": "grid",  # grid, list, or custom
        "grid_columns": 4,
        "widgets": [
            "system_health",
            "user_metrics", 
            "device_metrics",
            "community_metrics",
            "recent_activity",
            "performance_charts",
            "security_alerts",
            "quick_actions",
        ],
    },
    
    # ========== FORM & INPUT STYLING ==========
    "FORMS": {
        "input_style": "modern",  # modern, classic, minimal
        "focus_border_color": "blue-500",
        "error_border_color": "red-500",
        "success_border_color": "green-500",
        "border_radius": "lg",
        "field_spacing": "md",
        "label_weight": "semibold",
        "help_text_size": "sm",
        "help_text_color": "gray-500",
    },
    
    # ========== TABLE & LIST CONFIGURATION ==========
    "TABLES": {
        "striped": True,
        "hover": True,
        "bordered": False,
        "compact": False,
        "row_actions": True,
        "bulk_actions": True,
        "sortable": True,
        "filterable": True,
        "pagination_size": "md",
        "row_height": "comfortable",  # compact, comfortable, spacious
    },
    
    # ========== ACTION BUTTONS ==========
    "ACTIONS": {
        "primary_color": "blue",
        "secondary_color": "gray",
        "success_color": "green", 
        "warning_color": "yellow",
        "error_color": "red",
        "button_sizes": {
            "xs": "0.5rem 0.75rem",
            "sm": "0.75rem 1rem",
            "md": "1rem 1.5rem", 
            "lg": "1.25rem 2rem",
            "xl": "1.5rem 2.5rem",
        },
        "icon_sizes": {
            "xs": "0.75rem",
            "sm": "1rem",
            "md": "1.25rem",
            "lg": "1.5rem",
            "xl": "2rem",
        },
    },
    
    # ========== NOTIFICATION SYSTEM ==========
    "NOTIFICATIONS": {
        "position": "top-right",  # top-right, top-left, bottom-right, bottom-left
        "timeout": 5000,
        "animation": "slide",  # slide, fade, scale
        "max_visible": 5,
        "types": {
            "success": {
                "icon": "check_circle",
                "color": "green",
                "background": "green-50",
                "border": "green-200",
            },
            "error": {
                "icon": "error",
                "color": "red", 
                "background": "red-50",
                "border": "red-200",
            },
            "warning": {
                "icon": "warning",
                "color": "yellow",
                "background": "yellow-50",
                "border": "yellow-200",
            },
            "info": {
                "icon": "info",
                "color": "blue",
                "background": "blue-50",
                "border": "blue-200",
            },
        },
    },
    
    # ========== SEARCH CONFIGURATION ==========
    "SEARCH": {
        "enabled": True,
        "placeholder": "Search across all models and applications...",
        "min_length": 2,
        "debounce": 300,
        "highlight_results": True,
        "search_fields": {
            "auth.user": ["username", "email", "first_name", "last_name"],
            "main.ritoaccount": ["rito_id", "user__username"],
            "main.device": ["ieda", "mac_address"],
            "main.communitymember": ["name", "email", "user_id"],
            "main.question": ["title", "content", "author__name"],
        },
    },
    
    # ========== EXPORT & IMPORT FEATURES ==========
    "EXPORT": {
        "formats": ["csv", "xlsx", "json", "pdf"],
        "max_rows": 10000,
        "include_images": False,
        "batch_size": 1000,
    },
    "IMPORT": {
        "max_file_size": 10485760,  # 10MB
        "allowed_formats": ["csv", "xlsx", "json"],
        "batch_size": 100,
        "validation_strict": True,
    },
    
    # ========== ADVANCED FEATURES ==========
    "FEATURES": {
        "dark_mode_toggle": True,
        "responsive_design": True,
        "keyboard_shortcuts": True,
        "bulk_operations": True,
        "inline_editing": True,
        "ajax_loading": True,
        "real_time_updates": True,
        "progressive_loading": True,
        "offline_support": False,
        "pwa_support": False,
    },
    
    # ========== CUSTOM COMPONENTS ==========
    "COMPONENTS": {
        "charts": {
            "enabled": True,
            "library": "chartjs",  # chartjs, apexcharts, or custom
            "colors": ["primary", "secondary", "accent", "success", "warning", "error"],
            "default_type": "line",  # line, bar, pie, doughnut
        },
        "maps": {
            "enabled": True,
            "provider": "openstreetmap",  # openstreetmap, google, mapbox
            "default_zoom": 10,
            "cluster_points": True,
        },
        "rich_text": {
            "enabled": True,
            "editor": "quill",  # quill, tinymce, or basic
            "toolbar": ["bold", "italic", "underline", "link", "list", "code"],
        },
        "file_upload": {
            "enabled": True,
            "max_size": 52428800,  # 50MB
            "allowed_types": ["image/*", "application/pdf", "text/*"],
            "multiple": True,
            "drag_drop": True,
        },
    },
    
    # ========== PERFORMANCE OPTIMIZATIONS ==========
    "PERFORMANCE": {
        "lazy_loading": True,
        "cache_duration": 300,  # 5 minutes
        "database_optimization": True,
        "static_compression": True,
        "image_optimization": True,
        "query_optimization": True,
    },
    
    # ========== SECURITY FEATURES ==========
    "SECURITY": {
        "session_timeout": 3600,  # 1 hour
        "password_strength": "high",  # low, medium, high
        "two_factor_auth": False,
        "ip_whitelist": [],
        "rate_limiting": True,
        "csrf_protection": True,
        "xss_protection": True,
        "clickjacking_protection": True,
    },
    
    # ========== INTERNATIONALIZATION ==========
    "I18N": {
        "default_language": "en",
        "supported_languages": ["en", "es", "fr", "de", "hi", "zh"],
        "rtl_support": True,
        "localization": {
            "date_format": "YYYY-MM-DD",
            "time_format": "HH:mm:ss",
            "timezone": "UTC",
            "currency": "USD",
        },
    },
    
    # ========== ACCESSIBILITY ==========
    "ACCESSIBILITY": {
        "high_contrast": False,
        "larger_text": False,
        "screen_reader": True,
        "keyboard_navigation": True,
        "focus_indicators": True,
        "reduced_motion": False,
        "aria_labels": True,
    },
    
    # ========== CUSTOMIZATION HOOKS ==========
    "HOOKS": {
        "before_render": "Portal.settings.before_render_hook",
        "after_render": "Portal.settings.after_render_hook",
        "before_save": "Portal.settings.before_save_hook",
        "after_save": "Portal.settings.after_save_hook",
        "before_delete": "Portal.settings.before_delete_hook",
        "after_delete": "Portal.settings.after_delete_hook",
    },
    
    # ========== LOGIN & AUTHENTICATION ==========
    "LOGIN": {
        "image": lambda request: "/static/img/login-bg.svg",
        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "form_style": "card",  # card, minimal, modern
        "show_social_login": False,
        "show_remember_me": True,
        "show_forgot_password": True,
        "redirect_after": lambda request: reverse_lazy("admin:index"),
        "custom_css": """
            .login-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .login-card {
                backdrop-filter: blur(10px);
                background: rgba(255, 255, 255, 0.1);
            }
        """,
    },
    
    # ========== CUSTOM CSS & JAVASCRIPT ==========
    "CUSTOM_CSS": [
        "/static/css/admin-custom.css",
        "/static/css/charts.css",
        "/static/css/animations.css",
    ],
    "CUSTOM_JS": [
        "/static/js/admin-custom.js",
        "/static/js/charts.js",
        "/static/js/analytics.js",
    ],
    
    # ========== EXTENSIONS & PLUGINS ==========
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇺🇸",
                "es": "🇪🇸", 
                "fr": "🇫🇷",
                "de": "🇩🇪",
                "hi": "🇮🇳",
                "zh": "🇨🇳",
            },
        },
        "constance": {
            "enabled": True,
            "config_prefix": "AEGIS_",
        },
        "guardian": {
            "enabled": True,
            "object_permissions": True,
        },
        "simple_history": {
            "enabled": True,
            "track_changes": True,
        },
        "import_export": {
            "enabled": True,
            "formats": ["csv", "xlsx", "json"],
        },
    },
    
    # ========== DEBUG & DEVELOPMENT ==========
    "DEBUG": {
        "show_queries": False,
        "show_templates": False,
        "show_signals": False,
        "performance_monitoring": True,
        "error_tracking": True,
    },
}

# ========== ADVANCED DASHBOARD CALLBACK ==========

# ========== SAFE DASHBOARD CALLBACK ==========

def advanced_dashboard_callback(request, context):
    """
    Safe dashboard with conditional model imports
    """
    try:
        # Import models inside the function (only when called)
        from main.models import Device, RitoAccount, CommunityMember, Question, Answer, ContactMessage, Subscriber
        
        # Basic counts with error handling
        context.update({
            "total_devices": Device.objects.count(),
            "active_devices": Device.objects.filter(is_active=True).count(),
            "total_identities": RitoAccount.objects.count(),
            "total_community_members": CommunityMember.objects.count(),
            "total_questions": Question.objects.count(),
            "total_answers": Answer.objects.count(),
            "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
            "active_subscribers": Subscriber.objects.filter(is_active=True).count(),
        })
        
    except Exception as e:
        # Fallback if models aren't available
        context.update({
            "total_devices": 0,
            "active_devices": 0,
            "total_identities": 0,
            "total_community_members": 0,
            "total_questions": 0,
            "total_answers": 0,
            "unread_messages": 0,
            "active_subscribers": 0,
            "system_status": "initializing",
            "error": str(e)
        })
    
    return context

def get_registration_trend():
    """Generate device registration trend data"""
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    dates = []
    counts = []
    
    for i in range(30, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        count = Device.objects.filter(registered_at__date=date).count()
        dates.append(date.strftime('%Y-%m-%d'))
        counts.append(count)
    
    return {
        'labels': dates,
        'datasets': [{
            'label': 'Device Registrations',
            'data': counts,
            'borderColor': '#4f46e5',  # primary-600
            'backgroundColor': 'rgba(79, 70, 229, 0.1)',
            'borderWidth': 2,
            'fill': True,
            'tension': 0.4,
        }]
    }

def get_community_growth_data():
    """Generate community growth analytics"""
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    dates = []
    member_counts = []
    question_counts = []
    answer_counts = []
    
    for i in range(6, -1, -1):
        date = timezone.now().date() - timedelta(days=i*7)
        week_start = date - timedelta(days=6)
        
        new_members = CommunityMember.objects.filter(
            join_date__range=[week_start, date]
        ).count()
        
        new_questions = Question.objects.filter(
            created_at__date__range=[week_start, date]
        ).count()
        
        new_answers = Answer.objects.filter(
            created_at__date__range=[week_start, date]
        ).count()
        
        dates.append(f"Week {7-i}")
        member_counts.append(new_members)
        question_counts.append(new_questions)
        answer_counts.append(new_answers)
    
    return {
        'labels': dates,
        'datasets': [
            {
                'label': 'New Members',
                'data': member_counts,
                'borderColor': '#06b6d4',  # cyan-500
                'backgroundColor': 'rgba(6, 182, 212, 0.1)',
            },
            {
                'label': 'Questions',
                'data': question_counts,
                'borderColor': '#10b981',  # emerald-500
                'backgroundColor': 'rgba(16, 185, 129, 0.1)',
            },
            {
                'label': 'Answers',
                'data': answer_counts,
                'borderColor': '#8b5cf6',  # violet-500
                'backgroundColor': 'rgba(139, 92, 246, 0.1)',
            }
        ]
    }

def get_platform_engagement_data():
    """Generate platform engagement metrics"""
    from django.db.models import Count, Avg
    from django.db.models.functions import TruncDay
    
    # Daily active users (last 7 days)
    daily_active = []
    dates = []
    
    for i in range(6, -1, -1):
        date = (timezone.now() - timedelta(days=i)).date()
        active_count = CommunityMember.objects.filter(
            Q(questions__created_at__date=date) | 
            Q(answers__created_at__date=date) |
            Q(bookmarks__created_at__date=date)
        ).distinct().count()
        
        dates.append(date.strftime('%a'))
        daily_active.append(active_count)
    
    # Content distribution by category/topic
    topics_data = Question.objects.values('topics__name').annotate(
        count=Count('id')
    ).order_by('-count')[:8]
    
    topics_labels = [item['topics__name'] or 'Uncategorized' for item in topics_data]
    topics_counts = [item['count'] for item in topics_data]
    
    return {
        'daily_engagement': {
            'labels': dates,
            'datasets': [{
                'label': 'Daily Active Users',
                'data': daily_active,
                'borderColor': '#ec4899',  # pink-500
                'backgroundColor': 'rgba(236, 72, 153, 0.1)',
            }]
        },
        'content_distribution': {
            'labels': topics_labels,
            'datasets': [{
                'data': topics_counts,
                'backgroundColor': [
                    '#4f46e5', '#06b6d4', '#10b981', '#8b5cf6',
                    '#ec4899', '#f59e0b', '#ef4444', '#6b7280'
                ],
            }]
        }
    }

# ========== HOOK FUNCTIONS ==========

def before_render_hook(request, context):
    """Hook called before template rendering"""
    # Add real-time notification count
    if request.user.is_authenticated:
        context['unread_notifications'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
    
    # Add system status
    context['system_status'] = get_system_status()
    
    return context

def after_render_hook(request, response):
    """Hook called after template rendering"""
    # Add performance headers
    response['X-Frame-Options'] = 'DENY'
    response['X-Content-Type-Options'] = 'nosniff'
    
    return response

def before_save_hook(request, obj, form, change):
    """Hook called before saving an object"""
    # Auto-generate timestamps
    if hasattr(obj, 'created_at') and not obj.created_at:
        obj.created_at = timezone.now()
    if hasattr(obj, 'updated_at'):
        obj.updated_at = timezone.now()
    
    # Log changes for audit trail
    if change and hasattr(obj, 'log_change'):
        obj.log_change(request.user, form.changed_data)

def after_save_hook(request, obj, form, change):
    """Hook called after saving an object"""
    # Send notifications for important changes
    if change and hasattr(obj, 'send_update_notifications'):
        obj.send_update_notifications()

def before_delete_hook(request, obj):
    """Hook called before deleting an object"""
    # Create backup of important data
    if hasattr(obj, 'create_backup'):
        obj.create_backup()
    
    # Check deletion permissions
    if not request.user.has_perm(f'{obj._meta.app_label}.delete_{obj._meta.model_name}'):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

def after_delete_hook(request, obj):
    """Hook called after deleting an object"""
    # Log deletion for audit trail
    from django.contrib.admin.models import LogEntry, CHANGE
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=CHANGE,
        change_message='Deleted object'
    )

# ========== HELPER FUNCTIONS ==========

def get_system_status():
    """Get current system health status"""
    from django.db import connection
    from django.core.cache import cache
    
    status = {
        'database': 'healthy',
        'cache': 'healthy',
        'storage': 'healthy',
        'security': 'healthy',
        'overall': 'healthy'
    }
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        status['database'] = 'degraded'
        status['overall'] = 'degraded'
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 1)
        if cache.get('health_check') != 'ok':
            status['cache'] = 'degraded'
            status['overall'] = 'degraded'
    except Exception:
        status['cache'] = 'degraded'
        status['overall'] = 'degraded'
    
    return status

# ========== CUSTOM CONTEXT PROCESSORS ==========

def admin_context_processor(request):
    """Custom context processor for admin site"""
    context = {}
    
    if request.user.is_authenticated:
        # Add user-specific data
        context.update({
            'user_avatar': get_user_avatar(request.user),
            'user_permissions': get_user_permissions(request.user),
            'quick_actions': get_quick_actions(request.user),
        })
    
    # Add system-wide data
    context.update({
        'current_theme': get_user_theme(request),
        'system_version': 'Aegis v2.1.0',
        'support_email': 'support@aegis-innovative.com',
        'documentation_url': 'https://docs.aegis-innovative.com',
    })
    
    return context

def get_user_avatar(user):
    """Get user avatar URL"""
    # Implementation depends on your user model
    return f"/static/img/avatars/{user.username[0].lower()}.svg"

def get_user_permissions(user):
    """Get user permissions for UI customization"""
    return {
        'can_manage_users': user.has_perm('auth.change_user'),
        'can_view_analytics': user.has_perm('main.view_analytics'),
        'can_moderate_content': user.has_perm('main.moderate_content'),
        'can_manage_devices': user.has_perm('main.manage_devices'),
    }

def get_quick_actions(user):
    """Get quick actions based on user permissions"""
    actions = []
    
    if user.has_perm('main.add_ritoaccount'):
        actions.append({
            'title': 'Create Identity',
            'icon': 'fingerprint',
            'url': reverse_lazy('admin:main_ritoaccount_add'),
            'color': 'blue',
        })
    
    if user.has_perm('main.add_device'):
        actions.append({
            'title': 'Register Device',
            'icon': 'devices',
            'url': reverse_lazy('admin:main_device_add'),
            'color': 'green',
        })
    
    if user.has_perm('main.moderate_content'):
        actions.append({
            'title': 'Moderate Content',
            'icon': 'moderator',
            'url': reverse_lazy('admin:content_moderation'),
            'color': 'orange',
        })
    
    return actions

def get_user_theme(request):
    """Get user's preferred theme"""
    return request.COOKIES.get('theme', 'dark')

# ========== CUSTOM FILTERS & TAGS ==========

@register.filter
def format_number(value):
    """Format numbers with K/M suffixes"""
    if value >= 1000000:
        return f'{value/1000000:.1f}M'
    elif value >= 1000:
        return f'{value/1000:.1f}K'
    return str(value)

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return round((value / total) * 100, 1)

@register.simple_tag
def system_health_indicator(health_score):
    """Generate health indicator HTML"""
    if health_score >= 90:
        color = 'green'
        icon = 'check_circle'
    elif health_score >= 70:
        color = 'yellow'
        icon = 'warning'
    else:
        color = 'red'
        icon = 'error'
    
    return f'''
    <div class="health-indicator health-{color}">
        <span class="material-icons">{icon}</span>
        <span>{health_score}%</span>
    </div>
    '''

# ========== CUSTOM FILTERS & TAGS ==========

@register.filter
def format_number(value):
    """Format numbers with K/M suffixes"""
    if value >= 1000000:
        return f'{value/1000000:.1f}M'
    elif value >= 1000:
        return f'{value/1000:.1f}K'
    return str(value)

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return round((value / total) * 100, 1)

@register.simple_tag
def system_health_indicator(health_score):
    """Generate health indicator HTML"""
    if health_score >= 90:
        color = 'green'
        icon = 'check_circle'
    elif health_score >= 70:
        color = 'yellow'
        icon = 'warning'
    else:
        color = 'red'
        icon = 'error'
    
    return f'''
    <div class="health-indicator health-{color}">
        <span class="material-icons">{icon}</span>
        <span>{health_score}%</span>
    </div>
    '''


# Import-Export configuration
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = False
IMPORT_EXPORT_IMPORT_PERMISSION = True
IMPORT_EXPORT_EXPORT_PERMISSION = True