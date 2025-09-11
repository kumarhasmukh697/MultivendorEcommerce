from django.db import models
from accounts.models import User,UserProfile
from django.utils.text import slugify

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User,related_name='user',on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile,related_name='user_profile',on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        if not self.vendor_slug:
            self.vendor_slug = slugify(self.vendor_name)
        super().save(*args, **kwargs)





from django.db import models
from django.utils import timezone

class OpenHours(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('vendor', 'day_of_week')

    def is_open_now(self):
        # Get current time
        now = timezone.localtime()
        current_time = now.time()
        current_day = now.strftime('%A')

        if self.is_closed or self.day_of_week != current_day:
            return False

        if self.opening_time and self.closing_time:
            return self.opening_time <= current_time <= self.closing_time
        return False