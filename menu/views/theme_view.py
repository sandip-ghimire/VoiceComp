from .. import theme
from django.http import HttpResponse

def themechange(request):
    if request.method == 'POST':
        # global apptheme
        apptheme = request.POST.get("theme")
        print('apptheme: ' + apptheme)

        if apptheme == 'dark':
            theme_data = theme.dark
        elif apptheme == 'light':
            theme_data = theme.light

        response = HttpResponse('success')
        response.set_cookie('theme', theme_data)
        return response