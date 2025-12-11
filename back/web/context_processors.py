# back/web/context_processors.py
from django.conf import settings

def media_url(request):
    return {'MEDIA_BASE_URL': settings.MEDIA_BASE_URL}
