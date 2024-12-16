from django.contrib import admin
from .models import PasswordResetCode,Slider,Highlight,Blog

admin.site.register(PasswordResetCode)
admin.site.register(Slider)
admin.site.register(Highlight)
admin.site.register(Blog)

# Register your models here.
