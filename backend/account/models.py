from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.utils import timezone

import uuid


class MyUserManager(BaseUserManager):
    def create_user(self,email, name, password=None,**extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not name:
            raise ValueError('Users must have a name')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name,**extra_fields)
        user.set_password(password)
        user.save(using= self._db)
        return user


    def create_superuser(self,email, name, password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('email_verified',True)


        if extra_fields.get('is_staff') is not True:
            raise ValueError("SuperUser must have is_staff = True")

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("SuperUser must have is_superuser = True")

        
        return self.create_user(email,name,password,**extra_fields)

class MyUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True,verbose_name='email',max_length=255,db_index=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=150,verbose_name='name')
    phone_number = models.CharField(max_length=20, blank=True, default="")
    cart_items = models.JSONField(default=list, blank=True)
    wishlist_items = models.JSONField(default=list, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null =True, blank=True)

    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name
    def get_short_name(self):
        return self.name.split()[0] if self.name else self.email



class EmailVerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255,unique=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'email verification token'
        verbose_name_plural = 'email verification tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"Token for {self.user.email}: {self.token}"

    def is_valid(self):
        return not self.is_used and timezone.now()< self.expires_at

    def make_as_used(self):
        self.is_used = True
        self.save(update_fields=['is_used'])

    
class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='password_reset_tokens')
    token = models.CharField(max_length=255,unique=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'password reset token'
        verbose_name_plural = 'password reset tokens'
        ordering = ['-created_at']
    def __str__(self):
        return f"Password reset token for {self.user.email}: {self.token}"
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def make_as_used(self):
        self.is_used = True
        self.save(update_fields=['is_used'])


class LoginAttempt(models.Model):
    email = models.EmailField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField()
    successful = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'login attempt'
        verbose_name_plural = 'login attempts'
        ordering = ['-attempted_at']
    def __str__(self):
        status = "Successful" if self.successful else "Unsuccessful"
        return f"{status} login attempt for {self.email} from {self.ip_address} at {self.attempted_at}"


class Note(models.Model):
    """User notes model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.owner.email}"


# Backward-compatible alias for modules importing account.models.User
User = MyUser