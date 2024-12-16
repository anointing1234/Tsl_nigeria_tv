from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models.signals import post_save
import os
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image,UnidentifiedImageError
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.timezone import now


class Slider(models.Model):
    title = models.CharField(max_length=255, help_text="Title displayed on the slide")
    description = models.TextField(blank=True, help_text="Short description or content for the slide")
    image = models.ImageField(upload_to='slider_images/', help_text="Image displayed as the slide background")
    link = models.URLField(blank=True, null=True, help_text="URL to navigate to when the slide is clicked")
    order = models.PositiveIntegerField(default=0, help_text="Order in which the slide appears")
    is_active = models.BooleanField(default=True, help_text="Mark as true to display this slide")

    class Meta:
        ordering = ['order']
        verbose_name = "Slider"
        verbose_name_plural = "Sliders"

    def save(self, *args, **kwargs):
        if self.image:
            # Open the image file
            img = Image.open(self.image)

            # Convert to RGB mode if not already in it (WebP requires RGB)
            img = img.convert("RGB")

            # Create an in-memory BytesIO object for saving the image as WebP
            webp_image = BytesIO()

            # Save the image in WebP format with high quality
            img.save(webp_image, format='WEBP', quality=95)
            webp_image.seek(0)

            # Generate the WebP filename
            webp_name = os.path.splitext(self.image.name)[0] + '.webp'

            # Replace the image file with the WebP file
            self.image.save(webp_name, ContentFile(webp_image.read()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Highlight(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='highlights/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, default='Culture')

    def save(self, *args, **kwargs):
        # If an image is uploaded, process it
        if self.image:
            img = Image.open(self.image)
            
            # Convert image to .webp format for web optimization
            img = img.convert("RGB")
            webp_image = BytesIO()
            img.save(webp_image, format='WEBP', quality=85)  # Set the quality to 85 for a balance between quality and size
            webp_image.seek(0)
            
            # Save the image as a .webp file
            webp_name = os.path.splitext(self.image.name)[0] + '.webp'
            self.image.save(webp_name, ContentFile(webp_image.read()), save=False)
        
        # Call the parent class save method
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date']  # Most recent highlights first



class Blog(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    date = models.DateTimeField(default=now)
    author = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, default='Business')

    def save(self, *args, **kwargs):
        # Ensure the image exists and is accessible
        if self.image and not self._state.adding:  # Skip processing during initial creation
            try:
                img = Image.open(self.image)
                img = img.convert("RGB")
                webp_image = BytesIO()
                img.save(webp_image, format='WEBP', quality=85)
                webp_image.seek(0)
                webp_name = os.path.splitext(self.image.name)[0] + '.webp'
                self.image.save(webp_name, ContentFile(webp_image.read()), save=False)
            except Exception as e:
                # Log or handle the exception if needed
                print(f"Image processing failed: {e}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date']






class PasswordResetCode(models.Model):
    email = models.EmailField(max_length=254)  # Store the email address associated with the reset code
    reset_code = models.CharField(max_length=64)  # The reset code (should be securely generated)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the code was created
    expires_at = models.DateTimeField()  # Expiration time for the reset code

    def is_expired(self):
        """Check if the reset code is expired."""
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Reset code for {self.email}"        
    