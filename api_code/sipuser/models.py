from pickle import TRUE
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Domain(models.Model):

    name = models.CharField(verbose_name="name", max_length=100)
    domain = models.CharField(verbose_name="domain", max_length=100)
    description = models.CharField(verbose_name="Description", max_length= 250)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'fs_domain'
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'

    def __str__(self):
        return "%s" %self.name
    
class FsUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="auth_user")
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="user_domain")
    email = models.CharField(verbose_name="Email", max_length=100)
    cellphone = models.CharField(verbose_name="Cell Phonenumbers", max_length=20)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'fs_users'
        managed = True
        verbose_name = 'FS User'
        verbose_name_plural = 'FS Users'

    def __str__(self):
        return "%s" %self.user.username

class Extension(models.Model):

    user = models.ForeignKey(FsUser, on_delete=models.CASCADE, related_name="extension_user")
    sip_username = models.CharField(verbose_name="SIP Username", max_length=100)
    sip_password = models.CharField(verbose_name="SIP Password", max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'fs_extension'
        managed = True
        verbose_name = 'Extension'
        verbose_name_plural = 'Extensions'

    def __str__(self):
        return "%s" %self.sip_username

    def user_name(self):
        return self.user.user.username

class FsProvider(models.Model):

    name = models.CharField(verbose_name="Name", max_length=200)
    provider_type = models.CharField(verbose_name="Provider Type", help_text="ex. DID , Termimation", max_length=20)
    acl = models.CharField(verbose_name="IP Access List", help_text="command separate IP", max_length=200)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'fs_provider'
        managed = True
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'

    def __str__(self):
        return "%s" %self.name

class FsDidNumber(models.Model):

    provider = models.ForeignKey(FsProvider, on_delete=models.CASCADE, related_name="did_provider")
    phonenumber = models.CharField(verbose_name="DID Number", max_length=20)
    domain = models.ForeignKey(Domain,on_delete=models.CASCADE, null=TRUE)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'fs_didnumber'
        managed = True
        verbose_name = 'DID Number'
        verbose_name_plural = 'DID Numbers'

    def __str__(self):
        return "%s - %s" %(self.phonenumber, self.provider.name)

    def provider_name(self):
        return self.provider.name