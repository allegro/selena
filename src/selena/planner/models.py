#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from services.models import Service


class TechnicalBreak(models.Model):
    short_desciption = models.CharField(_('short description'), max_length=250)
    date_from = models.DateTimeField(_('date from'), db_index=True)
    date_to = models.DateTimeField(_('date to'), db_index=True)
    activated = models.BooleanField(
        _('activated'),
        default=False,
        db_index=True
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    def __unicode__(self):
        return "TechnicalBreak for %s" % (self.service.name)

    class Meta:
        verbose_name = _('Technical break')
        verbose_name_plural = _('Technical breaks')
