import random
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from .utils import encrypt_data, decrypt_data

class OTPStore(models.Model):
    """Stores OTPs for Email verification"""
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.email} - {self.otp}"

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    application_id = models.CharField(max_length=20, unique=True, primary_key=True, blank=True)
    status_choices = [
        (1, 'Submitted'),
        (2, 'Under Review'),
        (3, 'Approved'),
        (4, 'Completed'),
        (5, 'Rejected')
    ]
    status_level = models.IntegerField(choices=status_choices, default=1)
    applied_by_email = models.EmailField() # CHANGED: Now tracks by Email
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.application_id:
            date_str = timezone.now().strftime("%Y%m")
            rand_num = random.randint(100000, 999999)
            self.application_id = f"APP{date_str}S{rand_num}"
        super().save(*args, **kwargs)

class AadhaarApplication(BaseModel):
    name = models.CharField(max_length=100)
    aadhaar_number = models.CharField(max_length=255) 
    dob = models.DateField()
    old_mobile = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    new_mobile = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    document = models.FileField(upload_to='aadhaar_docs/')
    
    def save(self, *args, **kwargs):
        self.aadhaar_number = encrypt_data(self.aadhaar_number)
        super().save(*args, **kwargs)

    @property
    def decrypted_aadhaar(self):
        return decrypt_data(self.aadhaar_number)
        
    def __str__(self):
        return f"Aadhaar - {self.application_id} - {self.name}"

class PanApplication(BaseModel):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    mobile = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    identity_proof = models.FileField(upload_to='pan_docs/id/')
    address_proof = models.FileField(upload_to='pan_docs/address/')
    photo = models.ImageField(upload_to='pan_docs/photos/')

class VoterApplication(BaseModel):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    age = models.IntegerField()
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    mobile = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    constituency = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='voter_docs/photos/')
    proof = models.FileField(upload_to='voter_docs/proofs/')