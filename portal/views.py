import random
from datetime import timedelta
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import csv
from .models import OTPStore, AadhaarApplication, PanApplication, VoterApplication
from functools import wraps
from django.views.decorators.csrf import ensure_csrf_cookie
from .utils import generate_jwt, verify_jwt

# --- DECORATORS & MIDDLEWARE ---
def login_required_json(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('jwt_auth_token')
        email = verify_jwt(token)
        
        if not email:
            return JsonResponse({'error': 'Unauthorized. Invalid or Expired JWT Token.', 'status_code': 401}, status=401)
            
        request.jwt_email = email
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')

# --- AUTHENTICATION (EMAIL) ---
def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email or '@' not in email:
            return JsonResponse({'error': 'Invalid email address'}, status=400)
            
        # Rate Limiting
        recent_otp = OTPStore.objects.filter(email=email).first()
        if recent_otp and timezone.now() < recent_otp.created_at + timedelta(minutes=1):
            return JsonResponse({'error': 'Please wait 60 seconds before requesting another OTP.'}, status=429)
            
        otp_code = str(random.randint(100000, 999999))
        OTPStore.objects.update_or_create(email=email, defaults={'otp': otp_code})
        
        # SEND EMAIL LOGIC
        try:
            send_mail(
                subject='Your Citizen Portal Login OTP',
                message=f'Your One Time Password (OTP) for the Citizen Portal is: {otp_code}\n\nIt is valid for 5 minutes. Do not share this code with anyone.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            return JsonResponse({'message': 'OTP sent successfully'})
        except Exception as e:
            return JsonResponse({'error': f'Failed to send email. Ensure Gmail App Password is configured.'}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        entered_otp = request.POST.get('otp')
        
        try:
            record = OTPStore.objects.get(email=email)
            if timezone.now() > record.created_at + timedelta(minutes=5):
                return JsonResponse({'error': 'OTP Expired'}, status=400)
                
            if record.otp == entered_otp:
                record.delete()
                
                jwt_token = generate_jwt(email)
                
                request.session['email'] = email
                request.session['is_loaded'] = False 
                
                response = JsonResponse({'message': 'Login successful'})
                response.set_cookie(
                    'jwt_auth_token', 
                    jwt_token, 
                    httponly=True, 
                    samesite='Lax',
                    max_age=900
                )
                return response
                
            return JsonResponse({'error': 'Invalid OTP'}, status=400)
        except OTPStore.DoesNotExist:
            return JsonResponse({'error': 'Please request OTP first'}, status=400)

def logout_user(request):
    request.session.flush() 
    response = JsonResponse({'message': 'Logged out successfully'})
    response.delete_cookie('jwt_auth_token') 
    return response

def check_session(request):
    token = request.COOKIES.get('jwt_auth_token')
    email = verify_jwt(token)
    
    if email:
        return JsonResponse({'is_logged_in': True, 'email': email})
    return JsonResponse({'is_logged_in': False})

# --- APPLICATIONS ---
@login_required_json
def submit_aadhaar(request):
    if request.method == 'POST':
        try:
            app = AadhaarApplication.objects.create(
                applied_by_email=request.jwt_email, 
                name=request.POST.get('name'),
                aadhaar_number=request.POST.get('aadhaar_number'),
                dob=request.POST.get('dob'),
                old_mobile=request.POST.get('old_mobile'),
                new_mobile=request.POST.get('new_mobile'),
                email=request.POST.get('email', ''),
                address=request.POST.get('address'),
                document=request.FILES.get('document')
            )
            return JsonResponse({'message': 'Aadhaar App Submitted', 'app_id': app.application_id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required_json
def submit_pan(request):
    if request.method == 'POST':
        try:
            app = PanApplication.objects.create(
                applied_by_email=request.jwt_email,
                name=request.POST.get('name'),
                father_name=request.POST.get('father_name'),
                dob=request.POST.get('dob'),
                gender=request.POST.get('gender'),
                mobile=request.POST.get('mobile'),
                email=request.POST.get('email', ''),
                address=request.POST.get('address'),
                identity_proof=request.FILES.get('identity_proof'),
                address_proof=request.FILES.get('address_proof'),
                photo=request.FILES.get('photo')
            )
            return JsonResponse({'message': 'PAN App Submitted', 'app_id': app.application_id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required_json
def submit_voter(request):
    if request.method == 'POST':
        try:
            app = VoterApplication.objects.create(
                applied_by_email=request.jwt_email,
                name=request.POST.get('name'),
                father_name=request.POST.get('father_name'),
                age=request.POST.get('age'),
                dob=request.POST.get('dob'),
                gender=request.POST.get('gender'),
                mobile=request.POST.get('mobile'),
                email=request.POST.get('email', ''),
                address=request.POST.get('address'),
                constituency=request.POST.get('constituency'),
                photo=request.FILES.get('photo'),
                proof=request.FILES.get('proof')
            )
            return JsonResponse({'message': 'Voter App Submitted', 'app_id': app.application_id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# --- TRACKING & DOWNLOAD ---
def track_status(request):
    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        email = request.POST.get('email')
        
        app = None
        app_type = ""
        
        if AadhaarApplication.objects.filter(application_id=app_id, applied_by_email=email).exists():
            app = AadhaarApplication.objects.get(application_id=app_id)
            app_type = "Aadhaar Update"
        elif PanApplication.objects.filter(application_id=app_id, applied_by_email=email).exists():
            app = PanApplication.objects.get(application_id=app_id)
            app_type = "PAN Card"
        elif VoterApplication.objects.filter(application_id=app_id, applied_by_email=email).exists():
            app = VoterApplication.objects.get(application_id=app_id)
            app_type = "Voter ID"
            
        if app:
            return JsonResponse({
                'app_id': app.application_id,
                'name': app.name,
                'type': app_type,
                'date': app.created_at.strftime('%d %b %Y'),
                'statusLevel': app.status_level
            })
            
        return JsonResponse({'error': 'Application not found. Check details.'}, status=404)

def download_csv(request):
    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        email = request.POST.get('email')
        
        app = None
        app_type = ""
        
        if AadhaarApplication.objects.filter(application_id=app_id, applied_by_email=email).exists():
            app = AadhaarApplication.objects.get(application_id=app_id)
            app_type = "Aadhaar Update"
        elif PanApplication.objects.filter(application_id=app_id, applied_by_email=email).exists():
            app = PanApplication.objects.get(application_id=app_id)
            app_type = "PAN Card"
        elif VoterApplication.objects.filter(application_id=app_id, applied_by_email=email).exists():
            app = VoterApplication.objects.get(application_id=app_id)
            app_type = "Voter ID"
            
        if app:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{app_id}_Applicant_Data.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Application ID', 'Certificate Type', 'Applicant Name', 'Registered Email', 'Application Date', 'Status Level'])
            writer.writerow([
                app.application_id, 
                app_type, 
                app.name, 
                app.applied_by_email,
                app.created_at.strftime('%d %b %Y'), 
                f"Level {app.status_level}"
            ])
            return response
            
        return JsonResponse({'error': 'Application not found or unauthorized.'}, status=404)