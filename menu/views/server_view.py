import os
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, FileResponse
import logging
from django.conf import settings

@csrf_exempt
def audio_server(request, filename):
    logging.exception('AUDIOPATH:')
    logging.exception(os.path.join(settings.MEDIA_ROOT, filename))
    logging.exception('AUDIOPATHEND:')
    response = FileResponse(open(os.path.join(settings.MEDIA_ROOT, filename), "rb"))
    return response