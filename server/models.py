# Django Imports
from django.db import models
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.dispatch import receiver

# In Project Imports
from .validators import validate_image_icon_size,validate_image_file_extension

def category_icon_file_path(instance,filename):
    return f"category/{instance.id}/category_icon/{filename}"

def channel_icon_file_path(instance,filename):
    return f"channel/{instance.id}/channel_icon/{filename}"

def channel_banner_file_path(instance,filename):
    return f"channel/{instance.id}/channel_banner/{filename}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True,blank=True)
    icon = models.FileField(upload_to=category_icon_file_path,null=True,blank=True)

    def save(self, *args, **kwargs) -> None:
        if self.id:
            existing = get_object_or_404(Category,id=self.id)
            if existing.icon != self.icon:
                existing.icon.delete(save=False)

        super(Category,self).save(*args, **kwargs)
    
    @receiver(models.signals.pre_delete,sender="server.Category")
    def category_delete_files(sender,instance,**kwargs):
        for field in instance._meta.fields:
            if field.name == "icon":
                file = getattr(instance,field.name)
                if file:
                    file.delete(save=False)

    def __str__(self) -> str:
        return self.name
    
class Server(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="server_owner")
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="server_category")
    description = models.CharField(max_length=250,null=True,blank=True)
    member = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self) -> str:
        return self.name
    
class Channel(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="channel_owner")
    topic = models.CharField(max_length=100)
    server = models.ForeignKey(Server,on_delete=models.CASCADE,related_name="channel_server")
    banner = models.ImageField(upload_to=channel_banner_file_path,null=True,blank=True,validators=[validate_image_file_extension])
    icon = models.ImageField(upload_to=channel_icon_file_path,null=True,blank=True,validators=[validate_image_icon_size,validate_image_file_extension])

    def save(self, *args, **kwargs) -> None:
        self.name = self.name.lower()
        if self.id:
            existing = get_object_or_404(Channel,id=self.id)
            if existing.icon != self.icon:
                existing.icon.delete(save=False)
            if existing.banner != self.banner:
                existing.banner.delete(save=False)
        return super(Channel, self).save(*args, **kwargs)
    
    @receiver(models.signals.pre_delete,sender="server.Server")
    def channel_delete_files(sender,instance,**kwargs):
        for field in instance._meta.fields:
            if field.name == "icon" or field.name == "banner":
                file = getattr(instance,field.name)
                if file:
                    file.delete(save=False)

    def __str__(self) -> str:
        return self.name

    

