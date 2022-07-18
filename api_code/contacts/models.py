from django.db import models
from sipuser.models import Extension


class Phonebook(models.Model):

    extension = models.ForeignKey(Extension, on_delete=models.CASCADE, related_name="phonebook_extension")
    name = models.CharField(verbose_name="Phonebook Nmae", max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'phonebooks'
        managed = True
        verbose_name = 'Phonebook'
        verbose_name_plural = 'Phonebook'

    def __str__(self):
        return "%s" % self.name


CONTACT_CHOICES = (
    ("api", "api"),
    ("captcha", "captcha"),
    ("outbound", "outbound"),
)


class Contacts(models.Model):

    phonebook = models.ForeignKey(Phonebook, on_delete=models.CASCADE, related_name="contact_phonebook")
    phonenumber = models.CharField(verbose_name="Phonenumber", max_length=50)
    source = models.CharField(max_length=10, choices=CONTACT_CHOICES, default="API")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'contacts'
        managed = True
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

        unique_together = ('phonebook', 'phonenumber',)

    def __str__(self):
        return "%s - %s" % (self.phonenumber, self.phonebook)


class InboundNumbers(models.Model):

    phonenumber = models.CharField(verbose_name="Phonenumber", max_length=50)

    caller_type = models.CharField(max_length=100, default='')
    caller_carrier = models.CharField(max_length=100, default='')
    carrier_expired = models.DateTimeField(null=True)

    spam_risk = models.IntegerField(default=0)
    fraud_risk = models.IntegerField(default=0)
    unlawful_risk = models.IntegerField(default=0)
    spam_expired = models.DateTimeField(null=True)

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'inbound_number'
        managed = True
        verbose_name = 'Inbound Number'
        verbose_name_plural = 'Inbound Numbers'
        # unique_together = ('phonebook', 'phonenumber',)

    def __str__(self):
        return "%s - %s" % (self.phonenumber, self.caller_carrier)

    def save(self, *args, **kwargs):
        # from datetime import datetime, timedelta
        # self.expired_at = datetime.now() + timedelta(minutes=self.timeout)
        super(InboundNumbers, self).save(*args, **kwargs)
