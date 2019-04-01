# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    unique_value = models.CharField(max_length=50000)

class PhoneUsage(models.Model):
    application_name = models.CharField(max_length=50000,blank=True,null=True)
    last_used = models.DateTimeField(blank=True,null=True)
    hours_used = models.FloatField(blank=True,null=True)
    percentage = models.FloatField(blank=True,null=True)
    app_category = models.CharField(max_length=100000,blank=True,null=True)
    user = models.ForeignKey(User)

class Top5Apps(models.Model):
    applications = models.CharField(max_length=25000,blank=True,null=True)
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)


class Least5Apps(models.Model):
    applications = models.CharField(max_length=25000, blank=True, null=True)
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)

class NotificationHolder(models.Model):
    user = models.ForeignKey(User)
    notification_content = models.TextField(max_length=200000,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Query(models.Model):
    user = models.ForeignKey(User)
    text = models.CharField(max_length=250000,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)