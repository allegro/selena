#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from uuid import uuid4
from django.db import models
from services.models import Service


class Incident(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    incident_type = models.CharField(max_length=15, default='failure')
    is_closed = models.BooleanField(default=False, db_index=True)
    uuid = models.CharField(default=str(uuid4()), max_length=36)
