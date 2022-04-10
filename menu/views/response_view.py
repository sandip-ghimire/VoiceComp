
from ..models import Experiment, Worker, StarRating
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import ast

FIELD_MAP = {
    'task-interesting': 'rate_interest',
    'task-difficulty': 'rate_difficulty',
    'task-satisfaction': 'rate_satisfaction'
}

def optionselected(request):
    if request.method == 'POST':
        points = 0
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        worker_id = int(app_data.get('id'))
        worker = Worker.objects.get(pk=worker_id)
        score = float(worker.cur_score)

        response = request.POST.get("selectedchoice")
        ground_truth = request.POST.get("groundtruth")
        left_url = request.POST.get("leftid")
        right_url = request.POST.get("rightid")
        conf_percent = request.POST.get("conf_percent")
        level = request.POST.get("level")
        sp = request.POST.get("sp")
        dp = request.POST.get("dp")

        prev_left_url = request.session.get('leftUrl')
        prev_right_url = request.session.get('rightUrl')

        if left_url == prev_left_url and right_url == prev_right_url:
            return HttpResponse('success')

        request.session['leftUrl'] = left_url
        request.session['rightUrl'] = right_url
        points = float(sp) if ground_truth == 'same' else float(dp)
        if conf_percent and points:
            score += round((int(conf_percent)/100) * points, 2)

        if app_data and response and left_url and right_url and score and level:
            experiment = Experiment(
                batch_id=int(app_data.get('batch')),
                left_url=left_url,
                right_url=right_url,
                response_choice=response,
                ground_truth=ground_truth,
                confidence_percent=conf_percent,
                score=score,
                level=level
            )
            experiment.save()

            worker.cur_score = score
            worker.cur_level = level
            worker.save()

            return HttpResponse('success')
        else:
            return HttpResponse('failed')

def savelife(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        worker_id = int(app_data.get('id'))

        life = request.POST.get("life")
        fail = request.POST.get("fail")

        try:
            worker = Worker.objects.get(pk=worker_id)
            worker.cur_life = int(life)
            worker.cur_fail = int(fail)
            worker.save()
            return HttpResponse('success')
        except Exception:
            return HttpResponse('failed')

def resetgame(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        worker_id = int(app_data.get('id'))

        try:
            worker = Worker.objects.get(pk=worker_id)
            worker.cur_life = settings.TOTAL_LIFE
            worker.cur_fail = settings.TOTAL_FAIL
            worker.cur_score = 0
            worker.cur_level = settings.STARTING_LEVEL
            worker.save()
            return HttpResponse('success')
        except Exception:
            return HttpResponse('failed')

def setscore(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        worker_id = int(app_data.get('id'))
        score = request.POST.get("score")

        if score:
            try:
                worker = Worker.objects.get(pk=worker_id)
                worker.cur_score = score
                worker.save()
                return HttpResponse('success')
            except Exception:
                return HttpResponse('failed')
        return HttpResponse('failed')

def setlevel(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        worker_id = int(app_data.get('id'))
        level = request.POST.get("level")

        if level:
            try:
                worker = Worker.objects.get(pk=worker_id)
                worker.cur_level = level
                worker.save()
                return HttpResponse('success')
            except Exception:
                return HttpResponse('failed')
        return HttpResponse('failed')

def setrating(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        worker_id = int(app_data.get('id'))
        field = request.POST.get("field")
        model_field = FIELD_MAP.get(field)
        model_field_val = model_field+'_val'
        txt = request.POST.get("txt")
        value = request.POST.get("value")

        if model_field and txt and value:
            try:
                worker = Worker.objects.get(pk=worker_id)
                star_rating = worker.star_rating
                if star_rating:
                    setattr(star_rating, model_field, txt)
                    setattr(star_rating, model_field_val, int(value))
                    star_rating.save()
                else:
                    star_rating = StarRating(**{model_field: txt, model_field_val: int(value)})
                    star_rating.save()
                    worker.star_rating = star_rating
                    worker.save()
                return HttpResponse('success')
            except Exception:
                return HttpResponse('failed')
        return HttpResponse('failed')

def get_data_by_token(request):
    if request.method == 'POST':

        wtoken = request.POST.get("workertoken")
        wid = request.POST.get("workerid")
        resp = {}

        try:
            if wtoken:
                experiment = Experiment.objects.filter(code=wtoken).last()
                if experiment:
                    score = experiment.score
                    batch = experiment.batch
                    total_time = str(experiment.created_date - batch.created_date)
                    mturk_worker_id = batch.worker.alias_name
                    trials_count = batch.experiment_set.count()

                    resp.update({
                        "tscore": score,
                        "ttime": total_time,
                        "mtwid": mturk_worker_id,
                        "tcount": trials_count
                    })

                else:
                    return JsonResponse({"error": 'Worker token not found'})
            if wid:
                worker = Worker.objects.prefetch_related('batch_set').filter(alias_name=wid).last()
                if worker:
                    score = worker.cur_score
                    batch = worker.batch_set.last()
                    last_experiment = batch.experiment_set.last()
                    total_time = str(last_experiment.created_date - batch.created_date)
                    trials_count = batch.experiment_set.count()

                    resp.update({
                        "wscore": score,
                        "wtime": total_time,
                        "wcount": trials_count
                    })
                else:
                    return JsonResponse({"error": 'Worker with worker id not found'})

            return JsonResponse(resp)

        except Exception:
            return JsonResponse({"error": 'Unexpected error occured'})
