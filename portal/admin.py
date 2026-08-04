from django.contrib import admin
from .models import OTPStore, AadhaarApplication, PanApplication, VoterApplication

@admin.register(AadhaarApplication)
class AadhaarApplicationAdmin(admin.ModelAdmin):
    # These are the columns you will see in the list view
    list_display = ('application_id', 'name', 'aadhaar_number', 'status_level', 'created_at')
    # Adds a filter sidebar
    list_filter = ('status_level', 'created_at')
    # Adds a search bar that searches these fields
    search_fields = ('application_id', 'name', 'aadhaar_number', 'new_mobile')
    # Prevents accidental changes to these fields in the admin panel
    readonly_fields = ('application_id', 'created_at')

@admin.register(PanApplication)
class PanApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'name', 'mobile', 'status_level', 'created_at')
    list_filter = ('status_level', 'created_at')
    search_fields = ('application_id', 'name', 'mobile')
    readonly_fields = ('application_id', 'created_at')

@admin.register(VoterApplication)
class VoterApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'name', 'constituency', 'status_level', 'created_at')
    list_filter = ('status_level', 'created_at')
    search_fields = ('application_id', 'name', 'mobile', 'constituency')
    readonly_fields = ('application_id', 'created_at')

@admin.register(OTPStore)
class OTPStoreAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'created_at')
    search_fields = ('email',)