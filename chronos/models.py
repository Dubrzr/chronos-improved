from datetime import datetime
from itertools import chain
from _sha256 import sha224
from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    api_id = models.IntegerField(unique=True)
    parent_api_id = models.IntegerField(default=0)
    root = models.ForeignKey('self', null=True)


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    api_id = models.IntegerField()
    name = models.CharField(max_length=255)
    room = models.ForeignKey(to=Room)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()