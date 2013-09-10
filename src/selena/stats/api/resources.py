#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.db.models import Q
from django.utils import timezone
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.exceptions import ApiFieldError
from tastypie.resources import ModelResource

from stats.api.monkey import method_check
from stats.models import Incident, Service


# Monkeypatch Tastypie
# fix in https://github.com/toastdriven/django-tastypie/pull/863
ModelResource.method_check = method_check


class IncidentResource(ModelResource):
    class Meta:
        queryset = Incident.objects.all().order_by('start_date')
        resource_name = 'incidents'
        fields = ['id', 'start_date', 'end_date', 'is_closed', 'incident_type']
        allowed_methods = ['get']
        filtering = {
            'id': ['exact'],
            'start_date': ['exact', 'lte', 'gte'],
            'end_date': ['exact', 'lte', 'gte'],
            'service_name': ['exact'],
            'incident_type': ['exact'],
        }
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()

    def dehydrate_start_date(self, bundle):
        return timezone.localtime(
            bundle.data['start_date'],
        ).strftime("%Y-%m-%d %H:%M:%S")

    def dehydrate_end_date(self, bundle):
        return timezone.localtime(
            bundle.data['end_date'],
        ).strftime("%Y-%m-%d %H:%M:%S")


def _last_hour_incidents_filter_args():
    to_time = timezone.now()
    from_time = to_time - datetime.timedelta(hours=1)
    return [
        Q(start_date__gte=from_time, end_date__lte=to_time) |
        Q(start_date__gte=from_time, end_date__gt=to_time) |
        Q(start_date__lt=from_time, end_date__lte=to_time) |
        Q(start_date__lt=from_time, end_date__gt=to_time)
    ]


def _last_day_incidents_filter_args():
    current_date = timezone.now()
    to_date = datetime.datetime(year=current_date.year,
                                month=current_date.month,
                                day=current_date.day,
                                tzinfo=timezone.get_current_timezone())
    from_date = to_date - datetime.timedelta(days=1)
    return [
        Q(start_date__gte=from_date, end_date__lte=to_date) |
        Q(start_date__gte=from_date, end_date__gt=to_date) |
        Q(start_date__lt=from_date, end_date__lte=to_date) |
        Q(start_date__lt=from_date, end_date__gt=to_date)
    ]


def _last_hour_incidents_filter_kwargs():
    to_time = timezone.now()
    from_time = to_time - datetime.timedelta(hours=1)
    return {'start_date__lt': to_time, 'end_date__gt': from_time}


def _last_day_incidents_filter_kwargs():
    current_date = timezone.now()
    to_date = datetime.datetime(year=current_date.year,
                                month=current_date.month,
                                day=current_date.day,
                                tzinfo=timezone.get_current_timezone())
    from_date = to_date - datetime.timedelta(days=1)
    return {'start_date__lt': to_date, 'end_date__gt': from_date}


class CustomToManyField(fields.ToManyField):
    def __init__(self, to, attribute, filter_args_func=None,
                 filter_kwargs_func=None):
        super(CustomToManyField, self).__init__(to, attribute, full=True)
        self.filter_args_func = filter_args_func
        self.filter_kwargs_func = filter_kwargs_func

    def dehydrate(self, bundle):
        if not bundle.obj or not bundle.obj.pk:
            if not self.null:
                raise ApiFieldError(
                    "The model '%r' does not have a primary key and can not "
                    "be used in a ToMany context." % bundle.obj,
                )
            return []
        the_m2ms = None
        if isinstance(self.attribute, basestring):
            the_m2ms = getattr(bundle.obj, self.attribute)
        elif callable(self.attribute):
            the_m2ms = self.attribute(bundle)
        if not the_m2ms:
            if not self.null:
                raise ApiFieldError(
                    "The model '%r' has an empty attribute '%s' and doesn't "
                    "allow a null value." % (bundle.obj, self.attribute),
                )
            return []
        self.m2m_resources = []
        m2m_dehydrated = []
        for m2m in the_m2ms.filter(
                *self.filter_args_func(),
                **self.filter_kwargs_func()):
            m2m_resource = self.get_related_resource(m2m)
            m2m_bundle = Bundle(obj=m2m, request=bundle.request)
            self.m2m_resources.append(m2m_resource)
            m2m_dehydrated.append(
                self.dehydrate_related(m2m_bundle, m2m_resource),
            )

        return m2m_dehydrated


class ServiceResource(ModelResource):
    current_date = timezone.now()

    to_time = current_date
    from_time = to_time - datetime.timedelta(hours=1)

    last_hour_incidents = CustomToManyField(
        'stats.api.resources.IncidentResource',
        'incidents',
        filter_args_func=_last_hour_incidents_filter_args,
        filter_kwargs_func=_last_hour_incidents_filter_kwargs,
    )
    last_day_incidents = CustomToManyField(
        'stats.api.resources.IncidentResource',
        'incidents',
        filter_args_func=_last_day_incidents_filter_args,
        filter_kwargs_func=_last_day_incidents_filter_kwargs,
    )

    class Meta:
        queryset = Service.objects.filter(is_active=True)
        resource_name = 'services'
        fields = ['id', 'name', 'url']
        allowed_methods = ['get']
        filtering = {
            'id': ['exact'],
        }
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
