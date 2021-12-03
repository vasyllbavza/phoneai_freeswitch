from django.db import models

# Create your models here.
class CallStatus(models.IntegerChoices):
    PENDING = 0, 'Pending'
    CALLING = 1, 'Calling'
    ANSWERED = 2, 'Answered'
    PROCESSED = 3, 'Processed'
    SUCCESS = 4, 'Success'
    FAILED = 5, 'Failed'

class CallLog(models.Model):

    number = models.CharField(max_length=15, blank=True, null=True)
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

class CallKey(models.Model):

    call = models.ForeignKey(CallLog, on_delete=models.CASCADE)
    parent = models.IntegerField(null=True, blank=True)
    keys = models.CharField(max_length=5, blank=True, null=True)
    level = models.IntegerField(default=0)
    processed = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    audio_text = models.TextField(null=True, blank=True)
    audio_file = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} , {self.keys}"

    class Meta:
        db_table = 'call_keys'
        managed = True
        verbose_name = 'CallKey'
        verbose_name_plural = 'CallKeys'