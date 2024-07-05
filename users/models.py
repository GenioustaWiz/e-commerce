from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files import File
from urllib.request import urlopen
from io import BytesIO

from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField

# Custom UserManager to handle user creation and superuser creation
class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, request=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)

        # Generate username based on email if username is empty
        username = email.split('@')[0]

        user = self.model(
            email=email,
            # first_name=extra_fields.get('first_name', ''),
            # last_name=extra_fields.get('last_name', ''),
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, True, True, **extra_fields)

# Custom User model
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, blank=True, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Specify a related name for the groups field
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_profiles_groups',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )

    # Specify a related name for the user_permissions field
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_profiles_user_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    objects = UserManager()
    
    def __str__(self):
        return f'{self.email} User'

# UserProfile model to store additional user information
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = PhoneNumberField(null=True, blank=True)
    country = CountryField(null=True, blank=True)
    shipping_address = models.OneToOneField(ShippingAddress, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)
    wishlist = models.ManyToManyField('Product', blank=True)
    order_history = models.ForeignKey('Order', on_delete=models.SET_NULL, blank=True, null=True)
    ip_address = models.GenericIPAddressField(default="0.0.0.0")
    loyalty_points = models.IntegerField(default=0)  # Moved loyalty_points to UserProfile

    def __str__(self):
        return f'{self.user.email} Profile'

# Signal to handle social login and populate user profile
@receiver(pre_social_login, dispatch_uid='pre_social_login_signal')
@receiver(social_account_updated, dispatch_uid='social_account_updated_signal')
def populate_user_profile(sender, request, sociallogin, **kwargs):
    if sociallogin:
        user_data = sociallogin.account.extra_data
        email = user_data.get('email')
        user = User.objects.filter(email=email).first()

        # If user exists, get the profile, otherwise create a new user and profile
        if user:
            profile = user.profile
        else:
            user = User.objects.create_user(email=email, password=None, first_name=user_data.get('first_name', ''), last_name=user_data.get('last_name', ''))
            profile = UserProfile(user=user)

        profile.username = user_data.get('username', profile.user.username)

        # Fetch profile picture from social account provider
        if sociallogin.account.provider == 'facebook':
            image_url = f"http://graph.facebook.com/{sociallogin.account.uid}/picture?type=large"
        elif sociallogin.account.provider == 'linkedin':
            image_url = user_data.get('picture-urls', {}).get('picture-url', '')
        elif sociallogin.account.provider == 'twitter':
            image_url = user_data.get('profile_image_url', '').rsplit("_", 1)[0] + "." + user_data.get('profile_image_url', '').rsplit(".", 1)[1]
        elif sociallogin.account.provider == 'google':
            image_url = user_data.get('picture', '')
        elif sociallogin.account.provider == 'github':
            image_url = user_data.get('avatar_url', '')
        else:
            image_url = None

        # Save the profile picture if available
        if image_url:
            image_content = urlopen(image_url).read()
            image_file = BytesIO(image_content)
            profile.image.save('profile.jpg', File(image_file))

        profile.save()


