#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models

from services.models import Service


class Board(models.Model):
    name = models.CharField(max_length=250)
    services = models.ManyToManyField(Service)
