from ..models import PlayerInfo
from django.http import HttpResponse
import ast

def info_view(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)
        worker = ''
        if app_data:
            worker = app_data.get('worker')

        infoexp = request.POST.get("infoexp")
        infolang = request.POST.get("infolang")
        infodisability = request.POST.get("infodisability")
        infospeaker = request.POST.get("infospeaker")
        infobackground = request.POST.get("infobackground")
        infodevice = request.POST.get("infodevice")

        if worker and infoexp and infolang and infodisability and infospeaker and infobackground and infodevice:
            playerinfo = PlayerInfo(worker=worker, experience=infoexp, language=infolang, disability=infodisability, speaker=infospeaker, background=infobackground, device=infodevice)
            playerinfo.save()
            return HttpResponse('success')
        else:
            return HttpResponse('failed')
