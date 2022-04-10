from django.contrib import admin
from .models import Choices, Instructions, ChoicesGroup, ChoicesSet, Setting, Worker, Batch, Experiment, Feedback, PlayerInfo, StarRating

admin.site.register(Choices)
admin.site.register(Instructions)
admin.site.register(ChoicesGroup)
admin.site.register( ChoicesSet)
admin.site.register(Setting)
admin.site.register(Worker)
admin.site.register(Batch)
admin.site.register(Experiment)
admin.site.register(Feedback)
admin.site.register(PlayerInfo)
admin.site.register(StarRating)

