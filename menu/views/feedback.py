from ..models import Feedback
from django.http import HttpResponse
import ast

def feedback_view(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)
        worker = ''
        if app_data:
            worker = app_data.get('worker')

        rating = request.POST.get("rating")
        likefeed = request.POST.get("likefeed")
        dislikefeed = request.POST.get("dislikefeed")

        if worker and (rating or likefeed or dislikefeed):
            feedback = Feedback(worker=worker, rating=rating, likefeed=likefeed, dislikefeed=dislikefeed)   
            feedback.save()
            return HttpResponse('success')
        else:
            return HttpResponse('failed')