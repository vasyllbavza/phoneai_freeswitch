from django.db import models
from sipuser.models import Extension


class Phonebook(models.Model):

    extension = models.ForeignKey(Extension, on_delete=models.CASCADE, related_name="phonebook_extension")
    name = models.CharField(verbose_name="Phonebook Nmae", max_length=100, unique=True)
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
    ("API", "api"),
    ("CAPTCHA", "captcha"),
    ("OUTBOUND", "outbound"),
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
