# main/api.py
from ninja import NinjaAPI, Schema
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from typing import Optional, Dict, Any, List
from django.http import HttpRequest
import uuid
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Device, RitoAccount, SocialMediaAccount, generate_rito_id
from .utils import generate_registration_code, update_device_location, generate_username
from django.utils import timezone

# Create API instance with CSRF disabled
api = NinjaAPI(
    title="Rito API", 
    version="1.0.0",
    description="API for Rito device management and authentication",
    csrf=False  # Disable CSRF protection for API
)

# --- Schemas ---
class LoginSchema(Schema):
    username: str
    password: str

class RegisterDeviceSchema(Schema):
    ieda: str
    code: str
    username: Optional[str] = None

class CreateAccountSchema(Schema):
    ieda: str
    platform: str
    username: Optional[str] = None

class DeviceStatusSchema(Schema):
    ieda: str
    username: Optional[str] = None

class DeviceLocationSchema(Schema):
    ieda: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ip_address: Optional[str] = None
    username: Optional[str] = None

class SuccessSchema(Schema):
    status: str
    rito_id: Optional[str] = None
    username: Optional[str] = None
    registration_code: Optional[str] = None
    message: Optional[str] = None
    device_exists: Optional[bool] = None
    registered: Optional[bool] = None
    registered_to_user: Optional[bool] = None
    is_active: Optional[bool] = None
    last_seen: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    token: Optional[str] = None
    user_id: Optional[int] = None
    is_superuser: Optional[bool] = None

class ErrorSchema(Schema):
    status: str
    message: str

class TokenSchema(Schema):
    token: str
    user_id: int
    username: str
    is_superuser: bool

class DeviceInfoSchema(Schema):
    ieda: str
    rito_id: str
    registration_code: str
    is_active: bool
    last_seen: Optional[str] = None

class UserDevicesSchema(Schema):
    status: str
    username: str
    devices: List[DeviceInfoSchema]
    device_count: int
    message: str

# --- Authentication Endpoints ---

@api.post("/auth/login", response={200: TokenSchema, 401: ErrorSchema, 400: ErrorSchema})
def api_login(request: HttpRequest, credentials: LoginSchema):
    """
    API login endpoint for user authentication
    """
    try:
        user = authenticate(
            request, 
            username=credentials.username, 
            password=credentials.password
        )
        
        if user is not None:
            # Get or create token for the user
            token, created = Token.objects.get_or_create(user=user)
            return 200, {
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "is_superuser": user.is_superuser,
            }
        else:
            return 401, {"status": "error", "message": "Invalid credentials"}
            
    except Exception as e:
        return 400, {"status": "error", "message": f"Login failed: {str(e)}"}

@api.post("/auth/logout", response={200: SuccessSchema})
def api_logout(request: HttpRequest):
    """
    API logout endpoint
    """
    # If using token authentication, client should discard the token
    return 200, {"status": "success", "message": "Logged out successfully"}

# --- Enhanced Device Endpoints ---

@api.post("/device/register", response={200: SuccessSchema, 400: ErrorSchema})
def device_register_api(request: HttpRequest, data: RegisterDeviceSchema):
    """
    API endpoint for ESP8266 device registration with user support
    """
    try:
        if not data.ieda:
            return 400, {"status": "error", "message": "IEDA is required"}
        
        # Generate a new 6-digit registration code
        registration_code = generate_registration_code()
        
        # Check if device already exists
        device, created = Device.objects.get_or_create(
            ieda=data.ieda,
            defaults={
                'mac_address': f"MAC_{data.ieda[:8]}",
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
            "status": "success",
            "registration_code": registration_code,
            "device_exists": not created,
            "message": "Registration code generated successfully"
        }
        
        # Add user information to response if provided
        if data.username:
            response_data["requested_user"] = data.username
            response_data["message"] = f"Registration code generated for user {data.username}"
        
        return 200, response_data
        
    except Exception as e:
        return 400, {"status": "error", "message": f"Registration failed: {str(e)}"}

@api.post("/device/status", response={200: SuccessSchema, 400: ErrorSchema, 404: ErrorSchema})
def device_status_api(request: HttpRequest, data: DeviceStatusSchema):
    """
    API endpoint for device status check with user verification
    """
    try:
        if not data.ieda:
            return 400, {"status": "error", "message": "IEDA is required"}
        
        try:
            device = Device.objects.get(ieda=data.ieda)
            rito_account = RitoAccount.objects.filter(device=device).first()
            
            # Check if device is registered to the specific user
            registered_to_user = False
            user_rito_id = None
            
            if rito_account and data.username:
                registered_to_user = (rito_account.user.username == data.username)
                user_rito_id = rito_account.rito_id
            
            # Update last seen timestamp
            device.last_seen = timezone.now()
            device.save()
            
            response_data = {
                "status": "success",
                "registered": rito_account is not None,
                "registered_to_user": registered_to_user,
                "rito_id": user_rito_id,
                "registration_code": device.registration_code,
                "is_active": device.is_active,
                "last_seen": device.last_seen.isoformat()
            }
            
            # Add username info if available
            if rito_account and rito_account.user:
                response_data["username"] = rito_account.user.username
            
            # Custom message based on registration status
            if registered_to_user:
                response_data["message"] = f"Device registered to user {data.username}"
            elif rito_account and not registered_to_user:
                actual_user = rito_account.user.username
                response_data["message"] = f"Device registered to different user: {actual_user}"
            else:
                response_data["message"] = "Device not registered to any user"
            
            return 200, response_data
            
        except Device.DoesNotExist:
            return 404, {"status": "error", "message": "Device not found"}
            
    except Exception as e:
        return 400, {"status": "error", "message": f"Status check failed: {str(e)}"}

@api.post("/device/location", response={200: SuccessSchema, 400: ErrorSchema, 404: ErrorSchema})
def device_location_api(request: HttpRequest, data: DeviceLocationSchema):
    """
    API endpoint to update device location with user info
    """
    try:
        if not data.ieda:
            return 400, {"status": "error", "message": "IEDA is required"}
        
        try:
            device = Device.objects.get(ieda=data.ieda)
            
            # Update location data
            if data.latitude and data.longitude:
                device.latitude = float(data.latitude)
                device.longitude = float(data.longitude)
            
            location_updated = False
            if data.ip_address:
                device.ip_address = data.ip_address
                location_updated = update_device_location(device, data.ip_address)
            
            device.last_seen = timezone.now()
            device.save()
            
            response_data = {
                "status": "success",
                "message": "Location updated successfully",
            }
            
            # Add user info to response
            if data.username:
                response_data["user"] = data.username
            
            # Include location details if available
            if device.latitude and device.longitude:
                response_data["location"] = {
                    "latitude": device.latitude,
                    "longitude": device.longitude,
                    "city": device.city,
                    "country": device.country
                }
            
            return 200, response_data
            
        except Device.DoesNotExist:
            return 404, {"status": "error", "message": "Device not found"}
            
    except Exception as e:
        return 400, {"status": "error", "message": f"Location update failed: {str(e)}"}

# --- User-specific device registration ---

@api.post("/register", response={200: SuccessSchema, 400: ErrorSchema})
def register_device_web(request: HttpRequest, data: RegisterDeviceSchema):
    """
    Web registration endpoint with user association
    """
    try:
        # Check if device already exists
        if Device.objects.filter(ieda=data.ieda).exists():
            device = Device.objects.get(ieda=data.ieda)
            # Check if already registered to this user
            if RitoAccount.objects.filter(device=device).exists():
                return 400, {"status": "error", "message": "Device already registered"}
        
        # Create device
        device = Device.objects.create(
            ieda=data.ieda,
            mac_address="simulated_mac",
            registration_code=data.code
        )
        
        # Find user if username provided
        user = None
        if data.username:
            try:
                user = User.objects.get(username=data.username)
            except User.DoesNotExist:
                return 400, {"status": "error", "message": f"User {data.username} not found"}
        
        # Generate Rito ID and create account
        rito_id = generate_rito_id()
        account_data = {
            'device': device,
            'rito_id': rito_id,
            'name': f"{data.username}'s Account" if data.username else "Default Account"
        }
        
        if user:
            account_data['user'] = user
        
        RitoAccount.objects.create(**account_data)
        
        response_data = {
            "status": "success", 
            "rito_id": rito_id,
            "message": "Device registered successfully"
        }
        
        if data.username:
            response_data["username"] = data.username
            response_data["message"] = f"Device registered to user {data.username}"
        
        return 200, response_data
        
    except Exception as e:
        return 400, {"status": "error", "message": f"Registration failed: {str(e)}"}

@api.post("/create_account", response={200: SuccessSchema, 400: ErrorSchema})
def create_social_account(request: HttpRequest, data: CreateAccountSchema):
    """
    Create social media account endpoint
    """
    try:
        # Get device and Rito account
        device = get_object_or_404(Device, ieda=data.ieda)
        account = get_object_or_404(RitoAccount, device=device)
        
        # Check if social media account already exists
        if SocialMediaAccount.objects.filter(rito_account=account, platform=data.platform).exists():
            return 400, {"status": "error", "message": f"{data.platform.capitalize()} account already exists"}
        
        # Validate platform
        valid_platforms = [choice[0] for choice in SocialMediaAccount.PLATFORM_CHOICES]
        if data.platform not in valid_platforms:
            return 400, {
                "status": "error", 
                "message": f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
            }
        
        # Generate username and platform ID
        username = generate_username(data.platform, account.rito_id)
        platform_id = f"{data.platform}_{uuid.uuid4().hex[:8]}"
        
        # Create social media account
        SocialMediaAccount.objects.create(
            rito_account=account,
            platform=data.platform,
            platform_id=platform_id,
            username=username
        )
        
        return 200, {
            "status": "success", 
            "username": username,
            "message": f"{data.platform.capitalize()} account created successfully"
        }
        
    except Device.DoesNotExist:
        return 400, {"status": "error", "message": "Device not registered"}
    except Exception as e:
        return 400, {"status": "error", "message": f"Account creation failed: {str(e)}"}

@api.get("/ping", response=SuccessSchema)
def ping(request: HttpRequest):
    """
    Health check endpoint
    """
    return {"status": "success", "message": "pong"}

@api.get("/device/{ieda}/status", response={200: SuccessSchema, 404: ErrorSchema})
def device_status_web(request: HttpRequest, ieda: str):
    """
    Web endpoint to check device status
    """
    try:
        device = get_object_or_404(Device, ieda=ieda)
        account = get_object_or_404(RitoAccount, device=device)
        
        social_accounts = SocialMediaAccount.objects.filter(rito_account=account)
        platforms = [acc.platform for acc in social_accounts]
        
        return 200, {
            "status": "success",
            "rito_id": account.rito_id,
            "message": f"Registered platforms: {', '.join(platforms) if platforms else 'None'}"
        }
    except Device.DoesNotExist:
        return 404, {"status": "error", "message": "Device not found"}

# --- Additional utility endpoints ---

@api.post("/device/refresh-code", response={200: SuccessSchema, 400: ErrorSchema, 404: ErrorSchema})
def refresh_registration_code_api(request: HttpRequest, data: dict):
    """
    API endpoint to refresh registration code
    """
    try:
        ieda = data.get('ieda')
        
        if not ieda:
            return 400, {"status": "error", "message": "IEDA is required"}
        
        try:
            device = Device.objects.get(ieda=ieda)
            new_code = generate_registration_code()
            device.registration_code = new_code
            device.save()
            
            return 200, {
                "status": "success",
                "registration_code": new_code,
                "message": "Registration code refreshed successfully"
            }
            
        except Device.DoesNotExist:
            return 404, {"status": "error", "message": "Device not found"}
            
    except Exception as e:
        return 400, {"status": "error", "message": f"Code refresh failed: {str(e)}"}

@api.get("/user/{username}/devices", response={200: UserDevicesSchema, 404: ErrorSchema})
def get_user_devices(request: HttpRequest, username: str):
    """
    Get all devices registered to a specific user
    """
    try:
        user = get_object_or_404(User, username=username)
        rito_accounts = RitoAccount.objects.filter(user=user).select_related('device')
        
        devices = []
        for account in rito_accounts:
            if account.device:
                devices.append({
                    'ieda': account.device.ieda,
                    'rito_id': account.rito_id,
                    'registration_code': account.device.registration_code,
                    'is_active': account.device.is_active,
                    'last_seen': account.device.last_seen.isoformat() if account.device.last_seen else None
                })
        
        return 200, {
            "status": "success",
            "username": username,
            "devices": devices,
            "device_count": len(devices),
            "message": f"Found {len(devices)} devices for user {username}"
        }
        
    except User.DoesNotExist:
        return 404, {"status": "error", "message": f"User {username} not found"}

# --- API Documentation ---
@api.get("/docs", include_in_schema=False)
def api_docs(request: HttpRequest):
    """
    API documentation endpoint
    """
    return api.docsc