from django.conf import settings
from django.db import models
from django.utils import timezone


class Choices(models.Model):
    choice_id = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    value = models.IntegerField()
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        # Gives the proper plural name for admin
        verbose_name_plural = "Choices"

    def __str__(self):
        return self.title

class Instructions(models.Model):
    instruction_text = models.TextField()
    instruction_image = models.ImageField(upload_to="ins_image", default=None, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        # Gives the proper plural name for admin
        verbose_name_plural = "Instructions"

    def __str__(self):
        return self.instruction_text

class ChoicesGroup(models.Model):
    name = models.CharField(max_length=15)
    created_by = models.CharField(max_length=20)
    ctype = models.CharField(max_length=2)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'group-' + str(self.id) + ' | ' + 'created_by-' + self.created_by

class ChoicesSet(models.Model):
    choices_group = models.ForeignKey('ChoicesGroup', default=1, related_name='choicessets', on_delete=models.SET_DEFAULT)
    choices_id = models.ForeignKey('Choices', default=1, on_delete=models.SET_DEFAULT)
    samepoint = models.DecimalField(max_digits=4, decimal_places=1)
    differentpoint = models.DecimalField(max_digits=4, decimal_places=1)
    checked = models.CharField(max_length=10)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'group-' + str(self.choices_group.id) + ' : ' + self.choices_id.title

class Setting(models.Model):
    choices_group = models.ForeignKey('ChoicesGroup', related_name='settingsets', default=1, on_delete=models.SET_DEFAULT)
    instructions = models.ForeignKey('Instructions', default=1, on_delete=models.SET_DEFAULT)
    audio_files = models.FileField(upload_to="audio_files", default='audio_files/files.txt')
    score_files = models.FileField(upload_to="score_files", default='score_files/all_vs_all_scores.npy')
    truth_files = models.FileField(upload_to="truth_file", default='truth_file/ground_truth.npy')
    randomize_option = models.CharField(max_length=10, default='randomize')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'setting-' + str(self.id) + ' | ' + 'group-' + str(self.choices_group.id) + ' | ' + str(self.instructions.instruction_text)

class Worker(models.Model):
    name = models.CharField(max_length=20)
    alias_name = models.CharField(max_length=20, default='Unknown')
    cur_score = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    cur_level = models.IntegerField(default=1, blank=True, null=True)
    cur_life = models.IntegerField(default=3, blank=True, null=True)
    cur_fail = models.IntegerField(default=0, blank=True, null=True)
    star_rating = models.OneToOneField('StarRating', default=None, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class StarRating(models.Model):
    rate_interest = models.CharField(max_length=50, default=None, blank=True, null=True)
    rate_difficulty = models.CharField(max_length=50, default=None, blank=True, null=True)
    rate_satisfaction = models.CharField(max_length=50, default=None, blank=True, null=True)
    rate_interest_val = models.IntegerField(default=None, blank=True, null=True)
    rate_difficulty_val = models.IntegerField(default=None, blank=True, null=True)
    rate_satisfaction_val = models.IntegerField(default=None, blank=True, null=True)

    def __str__(self):
        return 'interest-' + (self.rate_interest or 'none') + ' | ' + 'difficulty-' + (self.rate_difficulty or 'none') + ' | ' + 'satisfaction-' + (self.rate_satisfaction or 'none')

class Batch(models.Model):
    setting = models.ForeignKey('Setting', default=1, on_delete=models.SET_DEFAULT)
    worker = models.ForeignKey('Worker', default=1, on_delete=models.SET_DEFAULT)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'batch-' + str(self.id) + ' | ' + 'setting-' + str(self.setting.id) + ' | ' + str(self.worker.name)

class Experiment(models.Model):
    batch = models.ForeignKey('Batch', default=1, on_delete=models.SET_DEFAULT)
    left_url = models.CharField(max_length=80)
    right_url = models.CharField(max_length=80)
    response_choice = models.CharField(max_length=30)
    ground_truth = models.CharField(max_length=10)
    confidence_percent = models.IntegerField()
    created_date = models.DateTimeField(default=timezone.now)
    score = models.DecimalField(max_digits=10, decimal_places=2)
    code = models.CharField(max_length=80, default=None, blank=True, null=True)
    level = models.IntegerField(default=None, blank=True, null=True)


    def __str__(self):
        return 'experiment-' + str(self.id) + ' | ' + 'batch-' + str(self.batch.id)

class Feedback(models.Model):
    worker = models.CharField(max_length=20)
    rating = models.CharField(max_length=5)
    likefeed = models.TextField()
    dislikefeed = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'feedback-' + str(self.id)

class PlayerInfo(models.Model):
    worker = models.CharField(max_length=20)
    experience = models.CharField(max_length=100)
    language = models.CharField(max_length=100)
    disability = models.CharField(max_length=100)
    speaker = models.CharField(max_length=100)
    background = models.CharField(max_length=100)
    device = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'playerinfo-' + str(self.id)

