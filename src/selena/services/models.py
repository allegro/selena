#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import base64
import decimal

from Crypto.Cipher import AES
from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models
from lck.django.choices import Choices
from lck.django.common.models import Named

from services.utils import get_salt


class Queue(Named):
    pass


class Agent(Named):
    is_main = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    queue = models.ForeignKey(
        Queue, on_delete=models.PROTECT, null=True, blank=True,
    )
    salt = models.CharField(max_length=16, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk or not self.salt:
            self.salt = get_salt()
        super(Agent, self).save(*args, **kwargs)


class AuthMethodChoices(Choices):
    _ = Choices.Choice

    none = _('no authentication')
    basic = _('basic')
    digest = _('digest')
    gss_negotiate = _('GSS negotiate')
    ntlm = _('NTLM')


class Service(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    url = models.URLField()
    url.validators = [MaxLengthValidator(200), ]
    response_code = models.PositiveSmallIntegerField(default=200)
    performance_issues_time = models.PositiveSmallIntegerField(
        editable=True,
        default=settings.DEFAULT_PARAMS_PERFORMANCE_ISSUES_TIME)
    connection_timeout = models.PositiveSmallIntegerField(
        editable=True,
        default=settings.DEFAULT_PARAMS_CONNECTION_TIMEOUT)
    service_working_min_probes_count = models.PositiveSmallIntegerField(
        default=settings.DEFAULT_SERVICE_WORKING_PROBES)
    time_delta = models.PositiveSmallIntegerField(
        default=settings.DEFAULT_TIME_DELTA)
    base_useragent = models.CharField(
        max_length=250,
        default=settings.DEFAULT_PARAMS_USERAGENT,
        verbose_name='Base USERAGENT')
    base_referer = models.URLField(
        blank=True,
        null=True,
        default=settings.DEFAULT_PARAMS_REFERER,
        verbose_name='Base REFERER')
    auth_user = models.CharField(max_length=250, blank=True, null=True)
    auth_pass = models.CharField(max_length=250, blank=True, null=True)
    is_active = models.BooleanField(editable=True, default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified = models.DateTimeField(auto_now_add=True, auto_now=True)
    is_technical_break = models.BooleanField(editable=True, default=False,
                                             db_index=True)
    is_core_service = models.BooleanField(editable=True, default=False,
                                          db_index=True)
    hosting = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=100)
    additional_agents = models.ManyToManyField(
        Agent,
        blank=True,
        null=True,
        help_text='Specify additional agents for this service.',
        limit_choices_to={'is_active': True},
    )
    sensitivity = models.DecimalField(
        help_text='Specify sensivity lever for this service. E.g. 0.25.',
        max_digits=3,
        decimal_places=2,
        default=decimal.Decimal(0.5),
    )
    auth_method = models.PositiveSmallIntegerField(
        db_index=True,
        choices=AuthMethodChoices(),
        default=AuthMethodChoices.none.id,
    )

    def _get_user(self):
        if self.auth_user is not None:
            cipher = AES.new(settings.AES_SECRET_KEY, AES.MODE_ECB)
            return cipher.decrypt(base64.b64decode(self.auth_user)).strip()
        return None

    def _set_user(self, value):
        if value is not None:
            cipher = AES.new(settings.AES_SECRET_KEY, AES.MODE_ECB)
            while len(value) % 16 != 0:
                value += ' '
            value = base64.b64encode(cipher.encrypt(value))
            self.auth_user = value
        else:
            self.auth_user = None

    user = property(_get_user, _set_user)

    def _get_password(self):
        if self.auth_pass is not None:
            cipher = AES.new(settings.AES_SECRET_KEY, AES.MODE_ECB)
            return cipher.decrypt(base64.b64decode(self.auth_pass)).strip()
        return None

    def _set_password(self, value):
        if value is not None:
            cipher = AES.new(settings.AES_SECRET_KEY, AES.MODE_ECB)
            while len(value) % 16 != 0:
                value += ' '
            value = base64.b64encode(cipher.encrypt(value))
            self.auth_pass = value
        else:
            self.auth_pass = None

    password = property(_get_password, _set_password)

    @property
    def incidents(self):
        return self.incident_set

    def __unicode__(self):
        return "%s (%s)" % (
            self.name.encode('ascii', 'ignore'),    # fix for RQ
            self.url,
        )

    class Meta:
        ordering = ['name']


class MonitoredPhrase(models.Model):
    phrase = models.CharField(max_length=250)
    shall_not_be = models.BooleanField(default=False)
    is_active = models.BooleanField(editable=True, default=True, db_index=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


class AdditionalRequestParam(models.Model):
    name = models.CharField(max_length=250)
    useragent = models.CharField(blank=True, max_length=250,
                                 verbose_name='USERAGENT')
    referer = models.URLField(blank=True, null=True, verbose_name='REFERER')
    post = models.CharField(blank=True, null=True, max_length=250)
    get = models.CharField(blank=True, null=True, max_length=250)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


class ResponseStateChoices(Choices):
    _ = Choices.Choice

    ok = _("OK")
    performance = _("Performance issues")
    die = _("Service is working incorrectly")
    wordcheck_error = _("Wordcheck error")
    agent_failed = _("No response from agent")


class ServiceHistory(models.Model):
    service_id = models.PositiveIntegerField(db_index=True)
    response_state = models.PositiveSmallIntegerField(
        db_index=True,
        choices=ResponseStateChoices(),
        default=ResponseStateChoices.ok.id,
    )
    request_params_id = models.PositiveIntegerField(null=True, blank=True)
    agent_id = models.PositiveIntegerField()
    response_code = models.PositiveSmallIntegerField(null=True, blank=True)
    response_time = models.DecimalField(
        blank=True,
        null=True,
        max_digits=5,
        decimal_places=2,
    )
    namelookup_time = models.DecimalField(blank=True, null=True, max_digits=5,
                                          decimal_places=2)
    connect_time = models.DecimalField(blank=True, null=True, max_digits=5,
                                       decimal_places=2)
    pretransfer_time = models.DecimalField(blank=True, null=True, max_digits=5,
                                           decimal_places=2)
    starttransfer_time = models.DecimalField(blank=True, null=True, max_digits=5,
                                             decimal_places=2)
    redirect_time = models.DecimalField(blank=True, null=True, max_digits=5,
                                        decimal_places=2)
    size_download = models.IntegerField(blank=True, null=True)
    speed_download = models.IntegerField(blank=True, null=True)
    redirect_count = models.PositiveSmallIntegerField(blank=True, null=True)
    num_connects = models.PositiveSmallIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False,
                                   db_index=True)
    main_probe = models.PositiveIntegerField(
        editable=False,
        default=0,
        db_index=True,
    )
    tick_failed = models.BooleanField(
        default=False,
    )

    def __unicode__(self):
        return "History item #%s" % self.service_id

    class Meta:
        ordering = ['-created']


class ServiceHistoryExtra(models.Model):
    service_history_id = models.BigIntegerField(db_index=True)
    effective_url = models.URLField(blank=True, null=True,
                                    max_length=500)
    error_msg = models.CharField(max_length=500, null=True, blank=True)
    wordchecks_errors = models.CharField(max_length=500, null=True, blank=True)


class ServiceHistoryArchive(models.Model):
    service_id = models.PositiveIntegerField(db_index=True)
    agent_id = models.PositiveIntegerField()
    response_time = models.DecimalField(max_digits=5, decimal_places=2)
    namelookup_time = models.DecimalField(blank=True, null=True, max_digits=5,
                                          decimal_places=2)
    connect_time = models.DecimalField(blank=True, null=True, max_digits=5,
                                       decimal_places=2)
    pretransfer_time = models.DecimalField(blank=True, null=True, max_digits=5,
                                           decimal_places=2)
    starttransfer_time = models.DecimalField(blank=True, null=True,
                                             max_digits=5, decimal_places=2)
    redirect_time = models.DecimalField(blank=True, null=True, max_digits=5,
                                        decimal_places=2)
    size_download = models.IntegerField(blank=True, null=True)
    speed_download = models.IntegerField(blank=True, null=True)
    redirect_count = models.PositiveSmallIntegerField(blank=True, null=True)
    num_connects = models.PositiveSmallIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=False, auto_now=False,
                                   db_index=True)

    def __unicode__(self):
        return "History item #%s" % self.service_id

    class Meta:
        ordering = ['-created']
