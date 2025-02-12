from django.db import models
from audiofield.fields import AudioField
from django.conf import settings
import os.path
from django.utils.html import format_html

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
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    retry_auto = models.IntegerField(default=0)
    max_attempt = models.IntegerField(default=10)

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
    audio_text_debug = models.TextField(null=True, blank=True)

    completed = models.BooleanField(default=False)

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

    next = models.ForeignKey(CallMenu, on_delete=models.CASCADE, null=True, blank=True, unique=False, related_name="next")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.id} , {self.keys}"

    class Meta:
        db_table = 'call_keys'
        managed = True
        verbose_name = 'CallKey'
        verbose_name_plural = 'CallKeys'

class AgentCallLog(models.Model):

    number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)
    menu = models.ForeignKey(CallMenu, on_delete=models.DO_NOTHING)
    uuid = models.CharField(max_length=250, blank=True, null=True)
    status = models.IntegerField(default=CallStatus.PENDING, choices=CallStatus.choices)
    forwarding_number = models.CharField(max_length=250, blank=False, null=False)

    audio_file = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.number} [{self.menu_id}]"

    def phonenumber(self):
        return f"{self.number.number}"

    def audio_file_player(self):
        """audio player tag for admin"""
        if self.audio_file:
            file_url = settings.MEDIA_URL + str(self.audio_file)
            player_string = '<a href="%s" target="_blank">Recording</a>' % (file_url)
            return format_html(player_string)

    audio_file_player.allow_tags = True
    audio_file_player.short_description = ('Audio file')

    class Meta:
        db_table = 'agentcall_logs'
        managed = True
        verbose_name = 'Agent Call Log'
        verbose_name_plural = 'Agent Call Logs'

class SMSStatus(models.IntegerChoices):
    PENDING = 0, 'Pending'
    QUEUE = 1, 'Queue'
    SUCCESS = 2, 'Success'
    FAILED = 3, 'Failed'

class SMSLog(models.Model):

    sms_to = models.CharField(max_length=20)
    sms_body = models.CharField(max_length=140)
    status = models.IntegerField(default=SMSStatus.PENDING, choices=SMSStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    sms_result = models.TextField(max_length=500, blank=True, null=True)
    sms_id = models.CharField(max_length=100, blank=True, null=True)
    dlr_code = models.IntegerField(default=0, help_text="https://support.flowroute.com/681766-Delivery-Receipt-Response-Codes")
    callback_url = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f"{self.sms_to} [{self.sms_body}]"

    class Meta:
        db_table = 'sms_logs'
        managed = True
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'

class IncomingSMS(models.Model):

    sms_from = models.CharField(max_length=20)
    sms_to = models.CharField(max_length=20)
    sms_body = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    smslog = models.ForeignKey(SMSLog, on_delete=models.CASCADE, null=True)
    sms_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.sms_from} [{self.sms_body}]"

    class Meta:
        db_table = 'incoming_sms'
        managed = True
        verbose_name = 'Incoming SMS Log'
        verbose_name_plural = 'Incoming SMS Logs'
