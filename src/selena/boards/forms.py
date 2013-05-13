#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms

from services.models import Service


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label='Start date',
        input_formats=['%Y-%m-%d'],
    )
    stop_date = forms.DateField(
        label='Stop date',
        input_formats=['%Y-%m-%d'],
    )


class DateAndTimeRangeForm(DateRangeForm):
    start_time = forms.TimeField(
        label='Start time',
        input_formats=['%H:%M'],
    )
    stop_time = forms.TimeField(
        label='Stop time',
        input_formats=['%H:%M'],
    )


class CSVErrorsReportForm(DateRangeForm):
    service = forms.ChoiceField(
        label='Service',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(CSVErrorsReportForm, self).__init__(*args, **kwargs)
        services = [('', '---')]
        services.extend(
            Service.objects.filter(
                is_active=True,
            ).values_list('id', 'name'),
        )
        self.fields['service'].choices = services
