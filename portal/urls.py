from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # Auth APIs
    path('api/send-otp/', views.send_otp, name='send_otp'),
    path('api/verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/logout/', views.logout_user, name='logout'),
    path('api/check-session/', views.check_session, name='check_session'),
    
    # Application APIs
    path('api/submit-aadhaar/', views.submit_aadhaar, name='submit_aadhaar'),
    path('api/submit-pan/', views.submit_pan, name='submit_pan'),
    path('api/submit-voter/', views.submit_voter, name='submit_voter'),
    
    # Tracking API
    path('api/track/', views.track_status, name='track_status'),
    path('api/download-csv/', views.download_csv, name='download_csv'),
]