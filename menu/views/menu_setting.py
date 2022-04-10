from django.shortcuts import render, redirect
from ..models import Choices, Instructions, Worker, ChoicesGroup, ChoicesSet, Setting, Batch, Experiment, PlayerInfo
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import permission_required
from decimal import Decimal
from collections import defaultdict
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
from tempfile import TemporaryFile
from django.utils.encoding import smart_str
import json
import csv
import ast
import pytz
import io
import os
import uuid
import numpy as np
from . import app_view
temp_addoptions = []
temp_matrix = TemporaryFile()

def settings_view(request):
    instructions = Instructions()
    temp_addoptions = []

    app_data = request.COOKIES.get('app_data')
    app_data = ast.literal_eval(app_data)

    if request.method == "POST":
        multiplecheck = request.POST.get("multiplecheckbox")
        instructionstxt = request.POST.get("instructiontxt")
        set = request.POST.get("set")
        audiolist = request.FILES.get("audiolist")
        audioscore = request.FILES.get('audioscore')
        randomization = request.POST.get("randomization")
        setval = request.POST.get("setval")
        ins_img = request.FILES.get('image')
        addop = request.POST.get("addop")
        if addop:
            temp_addoptions = ast.literal_eval(addop)

        username = "Anonymous"
        if request.user.is_authenticated and request.user.is_staff:
            username = request.user.username

        if multiplecheck == 'true':

            if instructionstxt:

                instructions.instruction_text = instructionstxt
                if ins_img:
                    instructions.instruction_image = ins_img

                instructions.save()
                app_data.update(instructions=instructions.pk)

                if not temp_addoptions:
                    if setval:
                        try:
                            setting_config = Setting.objects.get(pk=int(setval))
                            setting_config.instructions = instructions
                            setting_config.save()
                        except ObjectDoesNotExist:
                            setting_config = Setting(choices_group_id=int(app_data.get('group')), instructions=instructions)
                            setting_config.save()
                    else:
                        setting_config = Setting(choices_group_id=int(app_data.get('group')), instructions=instructions)
                        setting_config.save()
                    app_data.update(settings=setting_config.pk)


            if temp_addoptions:

                choices_group_count = ChoicesGroup.objects.count()
                if set:
                    choices_group_name = set
                else:
                    choices_group_name = 'Group-' + str(choices_group_count + 1)
                try:
                    choices_group = ChoicesGroup.objects.get(name=set, created_by=username)
                except ObjectDoesNotExist:
                    choices_group = ChoicesGroup(name=choices_group_name, created_by=username, ctype='gn')
                    choices_group.save()
                except ChoicesGroup.MultipleObjectsReturned:
                    return JsonResponse({'error': 'Multiple record with same setting name'})
                app_data.update(group=choices_group.pk)

                for option in temp_addoptions:
                    choices = Choices(choice_id='gn', title=option.get('name'), value=1)
                    choices.save()

                    choices_set = ChoicesSet(choices_group=choices_group,choices_id=choices, samepoint=float(option.get('samepoint')), differentpoint=float(option.get('differentpoint')), checked=option.get('checked'))
                    choices_set.save()

                if not instructionstxt:
                    if setval:
                        try:
                            setting_config = Setting.objects.get(pk=int(setval))
                            setting_config.choices_group = choices_group
                            setting_config.save()
                        except ObjectDoesNotExist:
                            setting_config = Setting(choices_group=choices_group, instructions_id=int(app_data.get('instructions')))
                            setting_config.save()
                    else:
                        setting_config = Setting(choices_group=choices_group, instructions_id=int(app_data.get('instructions')))
                        setting_config.save()
                    app_data.update(settings=setting_config.pk)


            if instructionstxt and temp_addoptions:
                if setval:
                    try:
                        setting_config = Setting.objects.get(pk=setval)
                        setting_config.choices_group = choices_group
                        setting_config.instructions = instructions
                        setting_config.save()
                    except ObjectDoesNotExist:
                        setting_config = Setting(choices_group=choices_group, instructions=instructions)
                        setting_config.save()
                else:
                    setting_config = Setting(choices_group=choices_group, instructions=instructions)
                    setting_config.save()
                app_data.update(settings=setting_config.pk)

            if set and not instructionstxt and not temp_addoptions:
                if app_data.get('group'):
                    cur_set = ChoicesGroup.objects.get(pk=int(app_data.get('group')))
                else:
                    cur_set = ChoicesGroup.objects.first()

                if set != cur_set.name:
                    try:
                        choices_group = ChoicesGroup.objects.get(name=set, created_by=username)
                        app_data.update(group=choices_group.pk)
                    except ObjectDoesNotExist:
                        return JsonResponse({'error': 'Save failed. Blank setting'})


                    if app_data.get('instructions'):
                        setting_config = Setting(choices_group=choices_group, instructions_id=int(app_data.get('instructions')))
                    else:
                        instruction = Instructions.objects.first()
                        setting_config = Setting(choices_group=choices_group, instructions=instruction)
                    setting_config.save()
                    app_data.update(settings=setting_config.pk)

            if setval:
                try:
                    setting_config = Setting.objects.get(pk=setval)
                    setting_config.created_date = timezone.now()
                    setting_config.save()
                    app_data.update(settings=setting_config.pk)
                except ObjectDoesNotExist:
                    pass

            if randomization:
                setting_config.randomize_option = randomization
                setting_config.save()

            if audiolist or audioscore:
                if (audiolist and audioscore) or (audiolist and randomization == 'sequential'):
                    audio_list = []
                    line = smart_str(audiolist.readline())
                    if line:
                        filepath = line.strip()
                        if "/" in filepath:
                            data = filepath.split("/")
                            folder_name = data[0]
                            file_name = data[-1]

                            if not folder_name.startswith('id') or not file_name.endswith('.wav'):
                                return JsonResponse({'error': 'Incorrect audio file content. File should contain list of audio path. Audio path format: "idxxxx/xxxx/xxxx.wav"'})

                        else:
                            return JsonResponse({'error': 'Audio file contains unusual data'})
                    else:
                        return JsonResponse({'error': 'Blank audio file'})

                    while line:
                        audio_list.append(line.strip())
                        line = smart_str(audiolist.readline())


                    if audio_list and not line:
                        n = len(audio_list)
                        if n < 10:
                            return JsonResponse({'error': 'Not enough data'})

                        if audioscore:

                            audio_score = np.load(audioscore)
                            if not (audio_score.ndim == 2 and audio_score.shape[0] == n and audio_score.shape[1] == n):
                                return JsonResponse({'error': 'Audio score shape is invalid. It should be shape=(n,n) where n is the length of audio list.'})

                            ground_truth_matrix = np.empty(shape=(n,n), dtype="U10")
                            for i, item_i in enumerate(audio_list):
                                matrix_list = []
                                for j, item_j in enumerate(audio_list):
                                    if i == j:
                                        matrix_list.append('diagonal')
                                    else:
                                        i_folder = ''
                                        j_folder= ''
                                        if "/" in item_j:
                                            data = item_j.split("/")
                                            j_folder = data[0]
                                        if "/" in item_i:
                                            data = item_i.split("/")
                                            i_folder = data[0]
                                        if i_folder and j_folder and i_folder == j_folder:
                                            matrix_list.append('same')
                                        elif i_folder and j_folder and i_folder != j_folder:
                                            matrix_list.append('different')
                                        else:
                                            matrix_list.append('not known')
                                ground_truth_matrix[i] = np.array(matrix_list)

                            np.save(temp_matrix, ground_truth_matrix)
                            setting_config.score_files = audioscore
                            setting_config.truth_files.save('ground_truth.npy', temp_matrix, save=False)

                        setting_config.audio_files = audiolist
                        setting_config.save()



                else:
                    return JsonResponse({'error': 'Please upload both files: audio list file and respective scores file'})

        else:
            if instructionstxt:
                instructions.instruction_text = instructionstxt
                instructions.save()
                app_data.update(instructions=instructions.pk)
            else:
                instructions = Instructions.objects.get(pk=int(app_data.get('instructions')))

            choices_group = ChoicesGroup.objects.first()
            app_data.update(group=choices_group.pk)

            setting_config = Setting(choices_group=choices_group, instructions=instructions)
            if randomization:
                setting_config.randomize_option = randomization
            setting_config.save()
            app_data.update(settings=setting_config.pk)

        response = JsonResponse({'success':'Setting saved'})
        response.set_cookie('app_data', app_data)
        return response



def addoptions_view(request):
    if request.method == 'POST':
        global temp_addoptions
        multiplecheck = request.POST.get("multiplecheck")
        addop = request.POST.get("addop")
        temp_data = ast.literal_eval(addop)

        if multiplecheck and temp_data:
            temp_addoptions = temp_data
            return HttpResponse('success')
    else:
        return redirect("choices_list")

def deletechoice(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        deleteoption = request.POST.get("deleteoption")
        multiplecheck = request.POST.get("multiplecheck")
        opid = request.POST.get("opid")

        if opid and multiplecheck and deleteoption:
            try:
                choices_set = ChoicesSet.objects.get(id=int(opid), choices_group_id=int(app_data.get('group')))
                choices_set.delete()
            except ObjectDoesNotExist:
                return HttpResponse('error')

            return HttpResponse('success')
    else:
        return redirect("choices_list")

def settings_shown(request):
    if request.method == 'POST':
        global temp_addoptions
        temp_addoptions = []
        username = settings.DEFAULT_CONTROL

        if request.user.is_authenticated and request.user.is_staff:
            username = request.user.username

        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        batch = Batch.objects.get(pk=int(app_data.get('batch')))
        batch_setting = Setting.objects.select_related('choices_group').get(pk=batch.setting_id)
        group_list = ChoicesGroup.objects.prefetch_related('choicessets__choices_id').prefetch_related('settingsets__instructions').filter(created_by=username, ctype='gn')
        set_list = defaultdict(list)
        for op in group_list:
            set_list[op.name].append(list(op.choicessets.filter(choices_group_id=op.id).values('id', 'choices_id__title', 'samepoint', 'differentpoint')))
            setting = op.settingsets.filter(choices_group_id=op.id).last()
            instruction = []
            data = {"text": "","url": ""}
            if setting:
                data["text"] = setting.instructions.instruction_text
                data["url"] = setting.instructions.instruction_image.url if setting.instructions.instruction_image else ''
            instruction.append(data)
            set_list[op.name].append(instruction)
            if setting:
                set_list[op.name].append([setting.id][0])
                set_list[op.name].append(setting.randomize_option)
                set_list[op.name].append(setting.audio_files.name)
                set_list[op.name].append(setting.score_files.name)
        returndata = json.dumps(set_list, cls=app_view.DecimalEncoder)

        return HttpResponse(returndata)

def rename_setting(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        oldname = request.POST.get("oldname")
        newname = request.POST.get("newname")
        username = 'Unknown'

        if request.user.is_authenticated and request.user.is_staff:
            username = request.user.username

        if oldname and newname:
            try:
                choices_group = ChoicesGroup.objects.get(name=oldname, created_by=username)
                choices_group.name = newname
                choices_group.save()
                return JsonResponse({"success": newname})
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Save failed. Setting doesn't exist"})

    else:
        return redirect("choices_list")

@permission_required('admin.can_add_log_entry')
def download_report(request):
    setting_name = request.GET.get("setting")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'
    localtimezone = pytz.timezone('Europe/Helsinki')
    # difficulty_list =[]
    fa = 0
    miss = 0
    target = 0
    non_target = 0
    conf = 0

    writer = csv.writer(response, delimiter=',')
    if setting_name:
        settings = Setting.objects.filter(choices_group__name=setting_name).last()
        if settings:
            batches = Batch.objects.filter(setting_id=settings.id)
            for batch in batches:
                batch_txt = '#Batch {0}, created on -{1}'.format(batch.id, batch.created_date.astimezone(localtimezone).strftime("%d-%B-%Y %H:%M:%S"))
                #batch_txt = '#Batch {0}'.format(batch.id)
                worker_info = PlayerInfo.objects.filter(worker=batch.worker.name)
                star_rating = batch.worker.star_rating
                if worker_info:
                    info_experience = 'Experience with voice comparison task before: {0}'.format(worker_info[0].experience)
                    info_language = 'Spoken language: {0}'.format(worker_info[0].language)
                    info_disability = 'Any hearing problem: {0}'.format(worker_info[0].disability)
                    info_speaker = 'Headphone/Loudspeakers: {0}'.format(worker_info[0].speaker)
                    info_background = 'Background noise: {0}'.format(worker_info[0].background)
                    info_device = 'Device used: {0}'.format(worker_info[0].device)
                if star_rating:
                    interest_rating = 'I find the task interesting: {0}'.format(star_rating.rate_interest)
                    interest_num = 'Rating for interest: {0}'.format(star_rating.rate_interest_val)
                    difficulty_rating = 'I would rate the difficulty of the task as: {0}'.format(star_rating.rate_difficulty)
                    difficulty_num = 'Rating for difficulty: {0}'.format(star_rating.rate_difficulty_val)
                    satisfaction_rating = 'I am happy about my performance: {0}'.format(star_rating.rate_satisfaction)
                    satisfaction_num = 'Rating for satisfaction: {0}'.format(star_rating.rate_satisfaction_val)

                    # extra
                    # difficulty_list.append(star_rating.rate_difficulty_val)
                    # d_list = 'List: {0}'.format(difficulty_list)
                    # d_total = 'Total: {0}'.format(len(difficulty_list))
                    # count_1 = 'count_1: {0}'.format(difficulty_list.count(1))
                    # count_2 = 'count_2: {0}'.format(difficulty_list.count(2))
                    # count_3 = 'count_3: {0}'.format(difficulty_list.count(3))

                experiments = Experiment.objects.filter(batch_id=batch.id)
                if experiments:
                    batch_txt += ' (Total trials = {0})'.format(experiments.count())
                    writer.writerow([batch_txt])
                    if worker_info:
                        writer.writerow([info_experience])
                        writer.writerow([info_language])
                        writer.writerow([info_disability])
                        writer.writerow([info_speaker])
                        writer.writerow([info_background])
                        writer.writerow([info_device])

                    if star_rating:
                        # writer.writerow([interest_rating])
                        writer.writerow([interest_num])
                        # writer.writerow([difficulty_rating])
                        writer.writerow([difficulty_num])
                        # writer.writerow([satisfaction_rating])
                        writer.writerow([satisfaction_num])

                        #extra
                        # writer.writerow([d_list])
                        # writer.writerow([d_total])
                        # writer.writerow([count_1])
                        # writer.writerow([count_2])
                        # writer.writerow([count_3])

                    writer.writerow(['CREATED TS',
                                     'WORKER',
                                     'LEVEL',
                                     'LEFT AUDIO',
                                     'RIGHT AUDIO',
                                     'USER RESPONSE',
                                     'GROUND TRUTH',
                                     'CONFIDENCE PERCENT',
                                     'GAME SCORE',
                                     'TOKEN',
                                     'MTURK_WORKER_ID',
                                     'SUCCESS/FAIL'])
                    for experiment in experiments:
                        writer.writerow([experiment.created_date.astimezone(localtimezone).strftime("%B-%d-%Y %H:%M:%S"),
                                         batch.worker.name,
                                         experiment.level,
                                         experiment.left_url,
                                         experiment.right_url,
                                         experiment.response_choice,
                                         experiment.ground_truth,
                                         experiment.confidence_percent,
                                         experiment.score,
                                         experiment.code,
                                         batch.worker.alias_name,
                                         1 if experiment.response_choice == experiment.ground_truth else 0])
                    #writer.writerow(['WORKER', 'LEFT AUDIO', 'RIGHT AUDIO', 'USER RESPONSE', 'GROUND TRUTH', 'CONFIDENCE PERCENT'])
                    #for experiment in experiments:
                        #writer.writerow([batch.worker.name, experiment.left_url, experiment.right_url, experiment.response_choice, experiment.ground_truth, experiment.confidence_percent])

                        conf += experiment.confidence_percent
                        if experiment.ground_truth == 'same':
                            target += 1
                            if experiment.response_choice == 'different':
                                miss += 1

                        if experiment.ground_truth == 'different':
                            non_target += 1
                            if experiment.response_choice == 'same':
                                fa += 1

                    writer.writerow([])
                    total_trials = experiments.count()
                    errors = miss+fa
                    error_rate = round((errors/total_trials)*100, 2)
                    missr = round((miss/target)*100, 2) if target else 0
                    far = round((fa/non_target)*100, 2) if non_target else 0
                    avg_conf = round(conf/total_trials, 2)
                    writer.writerow(['worker', 'missr', 'far', 'error_rate', 'misses', 'fa', 'total_trials', 'avg_confidence'])
                    writer.writerow([batch.worker.name, missr, far, error_rate, miss, fa, total_trials, avg_conf])
                    fa = 0
                    miss = 0
                    target = 0
                    non_target = 0
                    conf = 0

                    writer.writerow([])

            return response

def generatetoken(request):
    if request.method == 'POST':
        app_data = request.COOKIES.get('app_data')
        app_data = ast.literal_eval(app_data)

        worker = app_data.get('id')
        batch = app_data.get('batch')

        code = uuid.uuid4().hex[:8]
        amt_token = '{}w{}c{}'.format(batch, worker, code)
        try:
            experiment = Experiment.objects.filter(batch_id=int(batch)).last()
            if experiment.code:
                amt_token = experiment.code
            else:
                experiment.code = amt_token
                experiment.save()
            batch = experiment.batch
            hits = batch.experiment_set.count()
            return JsonResponse({"token": amt_token, "hits": hits})
        except Exception:
            return JsonResponse({"error": "Failed to generate token"})

