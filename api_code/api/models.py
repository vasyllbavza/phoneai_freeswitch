from django.db import models
from audiofield.fields import AudioField
from django.conf import settings
import os.path

# Create your models here.
class CallStatus(models.IntegerChoices):
    PENDING = 0, 'Pending'
    CALLING = 1, 'Calling'
    ANSWERED = 2, 'Answered'
    PROCESSED = 3, 'Processed'
    SUCCESS = 4, 'Success'
    FAILED = 5, 'Failed'

class PhoneNumber(models.Model):

    number = models.CharField(max_length=15, blank=True, null=True)
    business_name = models.TextField(null=True, blank=True)

    attempt = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'phone_numbers'
        managed = True
        verbose_name = 'Phonenumber'
        verbose_name_plural = 'Phonenumbers'

    def __str__(self) -> str:
        return super().__str__()

class CallLog(models.Model):

    number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=250, blank=True, null=True)
    status = models.IntegerField(default=CallStatus.PENDING, choices=CallStatus.choices)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.number} [{self.id}]"

    class Meta:
        db_table = 'call_logs'
        managed = True
        verbose_name = 'CallLog'
        verbose_name_plural = 'CallLogs'

class CallMenu(models.Model):

    call = models.ForeignKey(CallLog, on_delete=models.CASCADE)

    # Add the audio field to your model
    audio_file = AudioField(upload_to='', blank=True,
                        ext_whitelist=(".mp3", ".wav", ".ogg"),
                        help_text=("Allowed type - .mp3, .wav, .ogg"))
    audio_text = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    # Add this method to your model
    def audio_file_player(self):
        """audio player tag for admin"""
        if self.audio_file:
            file_url = settings.MEDIA_URL + str(self.audio_file)
            player_string = '<audio src="%s" controls>Your browser does not support the audio element.</audio>' % (file_url)
            return player_string

    audio_file_player.allow_tags = True
    audio_file_player.short_description = ('Audio file player')

    route_keys = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'call_menu'
        managed = True
        verbose_name = 'CallMenu'
        verbose_name_plural = 'CallMenus'

class CallKey(models.Model):

    menu = models.ForeignKey(CallMenu, on_delete=models.CASCADE, null=True)

    keys = models.CharField(max_length=5, blank=True, null=True)

    processed = models.IntegerField(default=0)

    audio_text = models.TextField(null=True, blank=True)
    audio_file = models.TextField(null=True, blank=True)

    next = models.OneToOneField(CallMenu, on_delete=models.CASCADE, null=True, blank=True, related_name="next")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.id} , {self.keys}"

    class Meta:
        db_table = 'call_keys'
        managed = True
        verbose_name = 'CallKey'
        verbose_name_plural = 'CallKeys'
