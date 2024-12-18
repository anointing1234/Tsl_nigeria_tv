from django.contrib import admin
from .models import PasswordResetCode,Slider,Highlight,Blog,LatestEvent,LatestEventHighlight,Showcase,Media

admin.site.register(PasswordResetCode)
admin.site.register(Slider)
admin.site.register(Highlight)
admin.site.register(Blog)
admin.site.register(LatestEvent)
admin.site.register(LatestEventHighlight)
admin.site.register(Showcase)
admin.site.register(Media)
