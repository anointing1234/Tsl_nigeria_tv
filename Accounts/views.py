from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth import logout
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetCode
import random
from datetime import timedelta
import logging
from django.utils.timezone import now
from .models import PasswordResetCode
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
import json



# Set up a logger instance
logger = logging.getLogger(__name__)



def register_view(request):
    if request.method == 'POST':
        # Get the form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')
        
        # Validate the form data
        if password != repeat_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'})
        
        if User.objects.filter(username=name).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists.'})
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists.'})
        
        # Create the user
        try:
            user = User.objects.create_user(username=name, email=email, password=password)
            user.save()
            # Authenticate the user and log them in
            user = authenticate(username=name, password=password)
            if user is not None:
                login(request, user)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'signup.html')  # Render the signup page if it's a GET request


def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('/') 

def login_views(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        logger.info(f"Login attempt: Username: {username}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            logger.info(f"Authentication successful for user: {username}")
            django_login(request, user)
            return JsonResponse({'success': True})
        else:
            logger.warning(f"Authentication failed for user: {username}")
            return JsonResponse({'success': False, 'error_message': 'Invalid credentials'})

    logger.warning("Invalid request method. Only POST requests are allowed.")
    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})


def send_password_reset_code(request):
    logger.info(f"Request method: {request.method}")
    
    if request.method == 'POST':
        email = request.POST.get('email')  # Extract email from POST data
        logger.info(f"Email received: {email}")

        if not email:
            logger.warning("Email field is empty.")
            return JsonResponse({
                'success': False,
                'error_message': 'Email field cannot be empty.',
            })

        if not User.objects.filter(email=email).exists():
            logger.warning(f"No user found with email: {email}")
            return JsonResponse({
                'success': False,
                'error_message': 'No user found with this email address.',
            })

        # Invalidate existing reset codes for this email
        PasswordResetCode.objects.filter(email=email, expires_at__gte=now()).delete()

        # Generate a random 6-digit reset code and expiration time
        reset_code = random.randint(100000, 999999)
        expires_at = now() + timedelta(hours=1)

        # Store the reset code in the database
        PasswordResetCode.objects.create(email=email, reset_code=str(reset_code), expires_at=expires_at)

        try:
            # Send email with the reset code
            send_mail(
                'Your Password Reset Code',
                f'Your password reset code is: {reset_code} (expires in 1 hour)',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            logger.info(f"Password reset email sent to {email}.")
        except Exception as e:
            logger.error(f"Failed to send reset email to {email}: {e}")
            return JsonResponse({
                'success': False,
                'error_message': 'Failed to send email. Please try again later.',
            })

        # Return a success response
        return JsonResponse({
            'success': True,
            'message': 'Password reset code sent successfully. Please check your email.',
        })

    # Return an error response for invalid request method
    logger.error("Invalid request method.")
    return JsonResponse({
        'success': False,
        'error_message': 'Invalid request method.',
    })



def reset_password(request):
    if request.method == 'POST':
        reset_code = request.POST.get('reset_code')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')

        # Validate the reset code and email
        try:
            # Check if the reset code exists and is valid
            reset_entry = PasswordResetCode.objects.get(email=email, reset_code=reset_code)

            if reset_entry.is_expired():
                return JsonResponse({'success': False, 'error_message': 'Reset code has expired.'})

            # If valid, reset the user's password
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # Log the password reset action
            logger.info(f"Password for {email} has been reset successfully.")

            # Optionally, delete the reset code after successful password reset
            reset_entry.delete()

            return JsonResponse({'success': True, 'message': 'Password has been reset successfully.'})

        except PasswordResetCode.DoesNotExist:
            logger.warning(f"Invalid reset code or email for {email}.")
            return JsonResponse({'success': False, 'error_message': 'Invalid reset code or email.'})
        except User.DoesNotExist:
            logger.warning(f"User  not found for email: {email}.")
            return JsonResponse({'success': False, 'error_message': 'User  not found.'})

    logger.error("Invalid request method.")
    return JsonResponse({'success': False, 'error_message': 'Invalid request method.'})






def contact_view(request):
    logger.info(f"Request method: {request.method}")

    if request.method == 'POST':
        # Get data sent from the form (JSON format)
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        logger.info(f"Received contact message from {name} ({email}) with subject: {subject}")

        # Check if required fields are provided
        if not name or not email or not subject or not message:
            logger.warning("Missing required fields in the contact form.")
            return JsonResponse({
                'success': False,
                'error_message': 'All fields are required.',
            })

        # Prepare the email content
        email_subject = f"New Contact Message: {subject}"
        email_message = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        recipient_email = 'yakubudestiny9@gmail.com'  # Replace with your recipient email

        try:
            # Send email using Django's send_mail function
            send_mail(
                email_subject,       # Email subject
                email_message,       # Email message
                settings.DEFAULT_FROM_EMAIL,  # Sender email
                [recipient_email],      # Receiver email
                fail_silently=False,
            )
            logger.info(f"Contact message sent successfully to {recipient_email}.")
            return JsonResponse({'success': True, 'message': 'Message sent successfully!'})

        except Exception as e:
            logger.error(f"Failed to send contact message: {e}")
            return JsonResponse({'success': False, 'message': 'Failed to send message.'})

    # Return error response for invalid request method
    logger.error("Invalid request method.")
    return JsonResponse({'success': False, 'message': 'Invalid request.'})