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
    
    




class LatestEvent(models.Model):
    title = models.CharField(max_length=200, help_text="The title of the event")
    description = models.TextField(help_text="A brief description of the event")
    image = models.ImageField(upload_to='event_images/', help_text="Event image")
    link = models.URLField(default="#", help_text="Link to event details")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the event was created")

    class Meta:
        verbose_name = "LatestEvents"
        verbose_name_plural = "LatestEvents"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Save the instance first to access the image
        super().save(*args, **kwargs)
        
        if self.image:
            img = Image.open(self.image)
            if img.format != 'WEBP':  # Avoid redundant conversion
                img = img.convert("RGB")  # Ensure compatibility for WebP
                output_io = BytesIO()
                img.save(output_io, format='WEBP', quality=85)  # High quality WebP (adjust quality as needed)
                self.image.save(f"{self.image.name.split('.')[0]}.webp", ContentFile(output_io.getvalue()), save=False)
                output_io.close()
                super().save(*args, **kwargs)     
    
    
    

class LatestEventHighlight(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the event highlight video")
    description = models.TextField(help_text="Brief description of the video")
    image = models.ImageField(upload_to='highlight_images/', help_text="Upload video thumbnail image")
    video_link = models.URLField(help_text="Link to the video details page")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "LatestHighlight"
        verbose_name_plural = "LatestHighlights"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Convert uploaded image to high-quality WebP
        if self.image:
            img_path = self.image.path
            filename, ext = os.path.splitext(img_path)
            webp_path = f"{filename}.webp"

            # Open the image and save as WebP
            img = Image.open(img_path)
            img.save(webp_path, "WEBP", quality=85)

            # Replace the old image with the new WebP file
            os.remove(img_path)
            self.image.name = self.image.name.replace(ext, ".webp")
            super().save(update_fields=["image"])

    def __str__(self):
        return self.title    
    
    
    
    

class Showcase(models.Model):
    title = models.CharField(max_length=100, help_text="Title for the showcase item.")
    image = models.ImageField(upload_to='showcase_images/', help_text="Upload the showcase image.")
    link = models.URLField(max_length=200, help_text="Link to the related blog or page.")
    display_order = models.PositiveIntegerField(default=0, help_text="Order of appearance in the carousel.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Showcase"
        verbose_name_plural = "Showcase"

    def save(self, *args, **kwargs):
        # Save the instance first to ensure an image file exists
        super().save(*args, **kwargs)
        
        if self.image:
            # Open the uploaded image
            image = Image.open(self.image)

            # Convert image to 'RGB' (necessary for saving in webp format)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Set the new file name and path with .webp extension
            image_filename = os.path.splitext(self.image.name)[0] + '.webp'

            # Save image to BytesIO in webp format
            webp_image_io = BytesIO()
            image.save(webp_image_io, format='WEBP', quality=90)  # Set quality as needed

            # Replace the original image with the webp version
            self.image.save(image_filename, ContentFile(webp_image_io.getvalue()), save=False)

            # Call the parent save to store the updated image
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title    
    
    
    

class Media(models.Model):
    title = models.CharField(max_length=100, help_text="Title for the media item.")
    description = models.TextField(max_length=300, help_text="Brief description of the media item.")
    image = models.ImageField(upload_to='media_section/', help_text="Upload the media image.")
    link = models.URLField(max_length=200, help_text="URL link to related content or blog.")
    display_order = models.PositiveIntegerField(default=0, help_text="Order of appearance in the carousel.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Media"
        verbose_name_plural = "Media"

    def save(self, *args, **kwargs):
        """Override save method to convert uploaded images to WebP format."""
        super().save(*args, **kwargs)  # Save the instance first

        if self.image:
            image = Image.open(self.image)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Create WebP version of the image
            image_filename = os.path.splitext(self.image.name)[0] + '.webp'
            webp_image_io = BytesIO()
            image.save(webp_image_io, format='WEBP', quality=90)

            # Replace the original image with the WebP version
            self.image.save(image_filename, ContentFile(webp_image_io.getvalue()), save=False)

            super().save(*args, **kwargs)  # Save the instance again with updated image

    def __str__(self):
        return self.title   
    