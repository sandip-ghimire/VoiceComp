from django.urls import path, re_path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views
from .views import app_view, menu_setting, login, response_view, theme_view, feedback, info, server_view

urlpatterns = [
    path('', app_view.choices_list, name='choices_list'),
    path('home', auth_views.LoginView.as_view(template_name='menu/choices_list.html'),{'next_page': '/index/'}, name='login'),
    path('index', auth_views.LogoutView.as_view(template_name='menu/choices_list.html'),{'next_page': '/'}, name='logout'),
    path('login', login.login_view, name='loginboard'),
    path('settings', menu_setting.settings_view, name='settings'),
    path('addoptions', menu_setting.addoptions_view, name='addoptions'),
    path('settingshow', menu_setting.settings_shown, name='settingshow'),
    path('renamesetting', menu_setting.rename_setting, name='renamesetting'),
    path('downloadreport', menu_setting.download_report, name='downloadreport'),
    path('themechange', theme_view.themechange, name='themechange'),
    path('optionselected', response_view.optionselected, name='optionselected'),
    path('savelife', response_view.savelife, name='savelife'),
    path('deletechoice', menu_setting.deletechoice, name='deletechoice'),
    path('feedback', feedback.feedback_view, name='feedback'),
    path('playerinfo', info.info_view, name='info'),
    path('audio/<path:filename>', server_view.audio_server, name='server'),
    path('generatetoken', menu_setting.generatetoken, name='generatetoken'),
    path('resetgame', response_view.resetgame, name='resetgame'),
    path('setscore', response_view.setscore, name='setscore'),
    path('setlevel', response_view.setlevel, name='setlevel'),
    path('setrating', response_view.setrating, name='setrating'),
    path('getdatabytoken', response_view.get_data_by_token, name='getdatabytoken'),

]