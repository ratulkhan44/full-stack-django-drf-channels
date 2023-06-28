# Django Imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# In Project Imports
from .models import Account
 

# Register your models here.
admin.site.register(Account,UserAdmin)
