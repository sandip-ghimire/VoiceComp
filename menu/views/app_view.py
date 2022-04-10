from django.shortcuts import render, redirect
from ..models import Choices, Instructions, Worker, ChoicesGroup, ChoicesSet, Setting, Batch, Experiment
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage
import random
import math
import os
import json
import ast
import pickle
import numpy as np
from django.core import serializers
from .. import theme
from decimal import Decimal
from django.db.models import Prefetch
from collections import defaultdict

from django.views.generic import TemplateView

def_choices = [{"name" : "same", "samepoint": 1, "differentpoint": 0}, {"name" : "different", "samepoint": 0, "differentpoint": 1}]
def_inst = "Are these voices same?"
audio_list = []
same_list = []
different_list = []
audio_file_directory = os.path.join(settings.MEDIA_ROOT, 'temp_data/')
audio_file = os.path.join(settings.MEDIA_ROOT, 'temp_data/temp.txt')

apptheme = settings.THEME if settings.GAMIFIED == 'true' else 'light'

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def choices_list(request):

    theme_cookie = request.COOKIES.get('theme')
    mturk_worker = request.GET.get("workerId")
    injected_worker = request.GET.get("survey")
    worker_alias = mturk_worker or injected_worker or 'Unknown'
    app_data = request.COOKIES.get('app_data')
    seq_cookie = request.COOKIES.get('seq')
    iseq_cookie = request.COOKIES.get('iseq')
    nxt = request.COOKIES.get('nxt')
    is_speaker = ['same', 'different']
    paths = []

    dark_theme = theme.dark
    light_theme = theme.light 
    speaker = random.choice(is_speaker)
    username = settings.DEFAULT_CONTROL
    confinst = settings.CONFIDENCE_INSTRUCTION
    appdata = {}
    setting_data = {}

    seq = settings.STARTING_SEQUENCE
    iseq = settings.NEXT_SEQUENCE
    lv = settings.STARTING_LEVEL
    lv_incr = settings.LEVEL_INCREMENT_INTERNALLY
    lv_multp = settings.LEVEL_MULTIPLY_INTERNALLY
    max_lv = settings.MAX_LEVEL

    max_level = (max_lv + lv_incr)*lv_multp

    if request.user.is_authenticated and request.user.is_staff:
        username = request.user.username

    if app_data is None:

        # Worker
        total_worker = Worker.objects.count()
        cur_worker = 'Worker' + str(total_worker + 1)
        worker = Worker(name=cur_worker, alias_name=worker_alias, cur_score=0, cur_level=lv, cur_life=settings.TOTAL_LIFE, cur_fail=settings.TOTAL_FAIL)
        worker.save()
        appdata.update(worker=cur_worker)
        appdata.update(id=worker.pk)
        worker_id = worker.pk
        request.session['leftUrl'] = 'none'
        request.session['rightUrl'] = 'none'

        try:
            setting_config = Setting.objects.filter(choices_group__created_by=username).latest('created_date')
            appdata.update(settings=setting_config.pk)
            appdata.update(instructions = setting_config.instructions_id)
            appdata.update(group = setting_config.choices_group_id)
        except ObjectDoesNotExist:
            # ChoicesGroup
            choices_group_count = ChoicesGroup.objects.count()
            choices_group_name = 'Group-' + str(choices_group_count + 1)
            choices_group = ChoicesGroup(name=choices_group_name, created_by=username, ctype='bi')
            choices_group.save()
            # group_id = choices_group.pk
            appdata.update(group = choices_group.pk)

            # Choices and ChoicesSet
            for choice in def_choices:
                choices = Choices(choice_id='bi', title=choice.get('name'), value=0)   
                choices.save()

                choices_set = ChoicesSet(choices_group=choices_group, choices_id=choices, samepoint=float(choice.get('samepoint')), differentpoint=float(choice.get('differentpoint')), checked='checked')
                choices_set.save()
            
            # Instructions
            instructions = Instructions(instruction_text=def_inst)
            instructions.save()
            # instructions_id = instructions.pk
            appdata.update(instructions=instructions.pk)

            # Setting
            setting_config = Setting(choices_group=choices_group, instructions=instructions)   
            setting_config.save()
            # settings_id = setting_config.pk
            appdata.update(settings=setting_config.pk)


        # Batch
        batch = Batch(setting=setting_config, worker=worker)   
        batch.save()
        # batch_id = batch.pk
        appdata.update(batch=batch.pk)

        cache_data(setting_config, worker_id)
        audio_file = audio_file_directory + 'temp' + str(worker_id) + '.txt'
        
    else:
        app_data = ast.literal_eval(app_data)
        worker_id = int(app_data.get('id'))
        audio_file = audio_file_directory + 'temp' + str(worker_id) + '.txt'


        try:
            batch = Batch.objects.get(pk=int(app_data.get('batch')))
        except ObjectDoesNotExist:
            url = reverse('choices_list')
            response = HttpResponseRedirect(url)
            response.delete_cookie('app_data')
            return response
     
    try:
        batch_setting = Setting.objects.select_related('choices_group').get(pk=batch.setting_id)
    except ObjectDoesNotExist:
        url = reverse('choices_list')
        response = HttpResponseRedirect(url)
        response.delete_cookie('app_data')
        return response

    created_by = batch_setting.choices_group.created_by
    if created_by != username:
        url = reverse('choices_list')
        response = HttpResponseRedirect(url)
        response.delete_cookie('app_data')
        return response
    new_setting = Setting.objects.select_related('choices_group').filter(choices_group__created_by=created_by).latest('created_date')
    if batch_setting.id != new_setting.id or batch.worker_id != worker_id:
        batch = Batch(setting_id=new_setting.id, worker_id=worker_id)   
        batch.save()
        if app_data:
            app_data.update(batch=batch.pk)
        if appdata:
            appdata.update(batch=batch.pk)

        cache_data(new_setting, worker_id)

    setting = Setting.objects.get(pk=batch.setting_id)
    worker = Worker.objects.get(pk=worker_id)
    life = worker.cur_life
    fail = worker.cur_fail
    worker_score = worker.cur_score
    worker_level = worker.cur_level
    lifelist = list(range(life))
    faillist = list(range(fail))

    if apptheme == 'dark':
        theme_data = theme.dark
    elif apptheme == 'light':
        theme_data = theme.light


    lv = int(worker_level)
    internal_lv = (lv + lv_incr) * lv_multp

    if seq_cookie:
        seq = int(seq_cookie)

    if iseq_cookie:
        iseq = int(iseq_cookie)

    try:
        set_theme = request.COOKIES.get('theme')
        set_theme = ast.literal_eval(set_theme)
    except (KeyError, ValueError):
        set_theme = theme_data

    np_load_old = np.load
    np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True)

    same_list = np.load(os.path.join(settings.MEDIA_ROOT, 'temp_data/same_list_with_score.npy'))
    different_list = np.load(os.path.join(settings.MEDIA_ROOT, 'temp_data/different_list_with_score.npy'))

    np.load = np_load_old

    try:
        with open(audio_file, "rb") as fp:
            audio_list = pickle.load(fp)
    except FileNotFoundError:
        url = reverse('choices_list')
        response = HttpResponseRedirect(url)
        response.delete_cookie('app_data')
        return response

    single_section_s = 0
    single_section_d = 0
    if len(same_list) > max_level:
        single_section_s = int(math.floor(len(same_list) / max_level))
    if len(different_list) > max_level:
        single_section_d = int(math.floor(len(different_list) / max_level))
    if internal_lv <= max_level:
        lindex_s = single_section_s * (internal_lv - 1)
        uindex_s = (single_section_s * internal_lv) if single_section_s > 0 else (len(same_list) - 1)
        lindex_d = single_section_d * (internal_lv - 1)
        uindex_d = (single_section_d * internal_lv) if single_section_d > 0 else (len(different_list) - 1)



    if setting.randomize_option == 'randomize':

        if speaker == 'same':
            rev_same_list = same_list[::-1]
            data_slice = rev_same_list[lindex_s:uindex_s]
            random_file = random.choice(data_slice)
            paths.append(random_file['left'])
            paths.append(random_file['right'])

            with open(os.path.join(settings.MEDIA_ROOT, 'temp_data/experimentrecord.txt'), 'a') as exprec:
                exprec.write(json.dumps(str(random_file)) + '\n')

        elif speaker == 'different':
            data_slice = different_list[lindex_d:uindex_d]
            random_file = random.choice(data_slice)
            paths.append(random_file['left'])
            paths.append(random_file['right'])

            with open(os.path.join(settings.MEDIA_ROOT, 'temp_data/experimentrecord.txt'), 'a') as exprec:
                exprec.write(json.dumps(str(random_file)) + '\n')

    else:
        if nxt == '1':
            seq = iseq
        i = seq
        for x in range(2):
            filepath = audio_list[i]
            if "/" in filepath:
                data = filepath.split("/")
                folder_name = data[0]
            paths.append(filepath)
            i += 1
            if x == 0:
                cache_foldername = folder_name
            else:
                if folder_name == cache_foldername:
                    speaker = 'same'
                else:
                    speaker = 'different'

                if (i > len(audio_list)-2):
                    i = 0

                print('length of audio list: ' + str(len(audio_list)))
                iseq = i



    audiopath = json.dumps(paths)
    audio_speaker = json.dumps(speaker)
   
    instructions = setting.instructions
    options = ChoicesSet.objects.select_related('choices_id').filter(choices_group_id=setting.choices_group_id)
    items = json.dumps({'data': list(options.values('id', 'choices_id__title', 'samepoint', 'differentpoint'))}, cls=DecimalEncoder)
    if options:
        isMultiple = 'true' if options[0].choices_id.choice_id == 'gn' else 'false'
        setting_data['defset'] = options[0].choices_group.name if isMultiple == 'true' else ''
        setting_data['setval'] = setting.id if isMultiple == 'true' else ''
        setting_data['rand'] = setting.randomize_option
        setting_data['aud'] = setting.audio_files.name
        setting_data['sco'] = setting.score_files.name
    
    else:
        Setting.objects.filter(choices_group__created_by=username).latest('created_date').delete()
        url = reverse('choices_list')
        response = HttpResponseRedirect(url)
        return response

    response = render(request, 'menu/choices_list.html',
                      {
                          'choices': options,
                          'instructions': instructions,
                          'audiopath': audiopath,
                          'speaker': audio_speaker,
                          'items': items,
                          'dark_theme': dark_theme,
                          'light_theme': light_theme,
                          'theme': set_theme,
                          'isMultiple': isMultiple,
                          'settingdata': setting_data,
                          'confinst': confinst,
                          'maxlv': max_lv,
                          'startlv': settings.STARTING_LEVEL,
                          'toaltrials_per_level': settings.TOTALTRIALS_PER_LEVEL,
                          'worker_score': worker_score,
                          'worker_level': worker_level,
                          'life': life,
                          'lifelist': lifelist,
                          'fail': fail,
                          'faillist': faillist,
                          'isGamified': settings.GAMIFIED,
                          'enableLife': settings.ENABLE_LIFE,
                          'url': settings.URL

                      })
    if theme_cookie is None:
        response.set_cookie('theme', theme_data)
    if settings.GAMIFIED == 'false':
        response.set_cookie('theme', theme.light)
    if app_data is None:
        response.set_cookie('app_data', appdata)
    else:
        response.set_cookie('app_data', app_data)
    response.set_cookie('nxt', 0)
    response.set_cookie('seq', seq)
    response.set_cookie('iseq', iseq)
    return response

def cache_data(setting, worker_id):
    audio_file = audio_file_directory + 'temp' + str(worker_id) + '.txt'
    file = setting.audio_files.path
    audio_list = []
    with open(file, 'r') as f:
        line = f.readline()
        cnt = 0
        while line:
            audio_list.append(line.strip())
            line = f.readline()
            cnt += 1

    if setting.randomize_option == 'shuffle':
        shuffled_tuple_list = []
        c = int(settings.TOTALTRIALS_PER_LEVEL)
        ev, od = audio_list[::2], audio_list[1::2]
        audio_list_tuples = list(zip(ev, od))

        for i in range(settings.MAX_LEVEL):
            list_partition = audio_list_tuples[i*c:(i+1)*c]
            random.shuffle(list_partition)
            shuffled_tuple_list.extend(list_partition)
        shuffle_list = [x for t in shuffled_tuple_list for x in t]
        with open(audio_file, "wb") as fp:
            pickle.dump(shuffle_list, fp)
    else:
        with open(audio_file, "wb") as fp:
            pickle.dump(audio_list, fp)

    if setting.randomize_option == 'randomize':
    
        allscores = np.load(os.path.join(settings.MEDIA_ROOT, setting.score_files.name))
        lower_triangle = np.tril(allscores, -1)
        ordered_index_list = np.argsort(lower_triangle, axis=None)
        tup = np.unravel_index(ordered_index_list, allscores.shape)
        ground_truth_matrix = np.load(os.path.join(settings.MEDIA_ROOT, setting.truth_files.name))

            
        for i, tup_i in enumerate(tup[0]):
            mapped_dict_same = {}
            mapped_dict_different = {}
            if lower_triangle[tup[0][i], tup[1][i]] > 0:
                if ground_truth_matrix[tup[0][i], tup[1][i]] == 'same':
                    mapped_dict_same['left'] = audio_list[tup[0][i]]
                    mapped_dict_same['right'] = audio_list[tup[1][i]]
                    mapped_dict_same['score'] = lower_triangle[tup[0][i], tup[1][i]]
                    same_list.append(mapped_dict_same)
                elif ground_truth_matrix[tup[0][i], tup[1][i]] == 'different':
                    mapped_dict_different['left'] = audio_list[tup[0][i]]
                    mapped_dict_different['right'] = audio_list[tup[1][i]]
                    mapped_dict_different['score'] = lower_triangle[tup[0][i], tup[1][i]]
                    different_list.append(mapped_dict_different)
            
        np.save(os.path.join(settings.MEDIA_ROOT, 'temp_data/same_list_with_score'), same_list)
        np.save(os.path.join(settings.MEDIA_ROOT, 'temp_data/different_list_with_score'), different_list)


    
