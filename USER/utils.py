# main/utils.py
import random
import string
import requests
from django.utils import timezone

def generate_registration_code():
    """Generate a 6-digit registration code"""
    return ''.join(random.choices(string.digits, k=6))

def update_device_location(device, ip_address=None):
    """Update device location based on IP address"""
    if not ip_address:
        return False
        
    device.ip_address = ip_address
    try:
        # Using ipapi.co for location data (free tier available)
        response = requests.get(f'http://ipapi.co/{ip_address}/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            device.latitude = data.get('latitude')
            device.longitude = data.get('longitude')
            device.city = data.get('city', '')
            device.country = data.get('country_name', '')
            device.save()
            return True
    except Exception as e:
        print(f"Location update failed: {e}")
    return False

def get_client_ip(request):
    """Get client IP address for location tracking"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_username(platform: str, rito_id: str) -> str:
    """
    Generate professional usernames for social media platforms
    """
    platform_prefixes = {
        'instagram': 'ig',
        'youtube': 'yt',
        'twitter': 'tw',
        'facebook': 'fb',
        'linkedin': 'li'
    }
    
    prefix = platform_prefixes.get(platform, platform[:2])
    clean_rito_id = rito_id.replace('-', '')[:8]
    
    return f"{prefix}_{clean_rito_id}"