from datetime import datetime, timedelta
import jwt

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from app.api.models import BaseModel, TenantModel

class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        
        # Ensure the user has a organization assigned
        if not hasattr(user, 'organization') or user.organization is None:
            user.organization = user._get_or_create_default_organization()
        
        user.save()

        return user

    def create_superuser(self, *args, **kwargs):
        """
        Create and return a `User` with superuser powers.

        Superuser powers means that this use is an admin that can do anything
        they want.
        """
        password = kwargs.pop('password', '')
        email = kwargs.pop('email', '')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.role = 'root'  # Set root role for superuser
        
        # Ensure the superuser has a organization assigned
        if not hasattr(user, 'organization') or user.organization is None:
            user.organization = user._get_or_create_default_organization()
        
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel, TenantModel):
    ROLE_CHOICES = [
        ('root', 'Root'),
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    first_name = models.CharField(db_index=True, max_length=255, unique=False)

    last_name = models.CharField(db_index=True, max_length=255, unique=False)

    surname = models.CharField(db_index=True, max_length=255, unique=False)

    username = models.CharField(
        db_index=True, max_length=255, unique=True, default="default-username")

    email = models.EmailField(db_index=True, unique=True)

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    is_email_active = models.BooleanField(default=False)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text="User role in the system"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'surname']

    objects = UserManager()


    def save(self, *args, **kwargs):
        """Override save method to handle organization assignment and root users."""
        
        # Determine whether the user already has a organization assigned without
        # triggering the descriptor (which raises when unset).
        has_organization= getattr(self, 'organization_id', None) is not None

        # For root users (superusers), handle organization assignment
        if self.is_superuser and self.role == 'root':
            if not has_organization:
                self.organization = self._get_or_create_default_organization()
        
        # For all other users, ensure they have a organization
        elif not has_organization:
            self.organization = self._get_or_create_default_organization()
        
        super().save(*args, **kwargs)
    

    def _get_or_create_default_organization(self):
        """Get or create a default organization for users."""
        from app.api.organization.models import Organization
        
        # First, try to find an existing default organization
        default_organization = Organization.objects.filter(
            models.Q(name='Default Organization') |
            models.Q(slug='default') 
        ).filter(is_active=True).first()
        
        if default_organization:
            return default_organization
        
        # If no default organization exists, create one
        try:
            default_organization = Organization.objects.create(
                name='Default organization',
                slug='default'
            )
            return default_organization
        except Exception as e:
            # If we can't create a organization, try to get any existing organization
            existing_organization = Organization.objects.filter(is_active=True).first()
            if existing_organization:
                return existing_organization
            else:
                # If no organization exist at all, this is a critical error
                raise Exception(f"Unable to create or find a default organization: {str(e)}")
    
    @property
    def token(self):
        """This method generates and returns a string of the token generated."""
        date = datetime.now() + timedelta(hours=settings.TOKEN_EXP_TIME)

        payload = {
            'email': self.email,
            'exp': int(date.strftime('%s')),
            'id': str(self.id),
            'ord': str(self.organization.id),
            "username": self.username
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token

    def __str__(self):
        return self.email
