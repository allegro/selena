#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import urlparse

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from services.helpers import Helper
from services.models import (
    AdditionalRequestParam,
    Agent,
    MonitoredPhrase,
    Queue,
    Service,
)
from services.validators import ExtendURLValidator


class MonitoredPhrasesInLine(admin.StackedInline):
    model = MonitoredPhrase
    extra = 0


class AdditionalRequestParamInlineFormset(BaseInlineFormSet):
    def clean(self):
        super(AdditionalRequestParamInlineFormset, self).clean()
        for form in self.forms:
            i = 0
            try:
                if form.cleaned_data['useragent']:
                    i += 1
                if form.cleaned_data['referer']:
                    i += 1
                if form.cleaned_data['post']:
                    i += 1
                    post_data = form.cleaned_data['post']
                    if post_data:
                        if not urlparse.parse_qsl(post_data):
                            raise ValidationError(
                                _(
                                    'POST parameters must be given by pattern '
                                    'variable "parameter=value" or '
                                    '"parameter1=value1&parameter2=value2" '
                                    'for many'
                                )
                            )
                if form.cleaned_data['get']:
                    i += 1
                    get_data = form.cleaned_data['get']
                    if get_data:
                        if not urlparse.parse_qsl(get_data):
                            raise ValidationError(
                                _(
                                    'GET parameters must be given by pattern '
                                    'variable "parameter=value" or '
                                    '"parameter1=value1&parameter2=value2" '
                                    'for many'
                                )
                            )
                if i == 0:
                    raise ValidationError(
                        _('Enter: USERAGENT, REFERER, POST or GET'),
                    )

            except AttributeError:
                pass
            except KeyError:
                pass


class AdditionalRequestParamInLine(admin.StackedInline):
    model = AdditionalRequestParam
    extra = 0
    formset = AdditionalRequestParamInlineFormset


class ServiceAdminForm(forms.ModelForm):
    user = forms.CharField(required=False, label=_('User'))
    password = forms.CharField(required=False, label=_('Password'))
    response_code = forms.CharField(
        max_length=3, initial=200, help_text=Helper().custom_status_helper(),
        label=_('Response code')
    )

    class Meta:
        model = Service

    def __init__(self, *args, **kwargs):
        super(ServiceAdminForm, self).__init__(*args, **kwargs)
        self.fields['url'].validators = [
            MaxLengthValidator(200),
            ExtendURLValidator(),
        ]
        if 'instance' in kwargs.keys():
            instance = kwargs['instance']
            self.initial['user'] = instance.user
            self.initial['password'] = instance.password

    def clean_performance_issues_time(self):
        performance_issues_time = self.cleaned_data['performance_issues_time']
        if performance_issues_time > 30:
            raise forms.ValidationError(_("Max acceptable value is 30."))
        return performance_issues_time

    def clean_connection_timeout(self):
        connection_timeout = self.cleaned_data['connection_timeout']
        if connection_timeout > 30:
            raise forms.ValidationError(_("Max acceptable value is 30."))
        return connection_timeout

    def clean_sensitivity(self):
        sensitivity = self.cleaned_data['sensitivity']
        if sensitivity > 1:
            raise forms.ValidationError(_("Max acceptable value is 1."))
        return sensitivity

    def save(self, commit=True):
        model = super(ServiceAdminForm, self).save(commit=False)
        model.user = self.cleaned_data['user']
        model.password = self.cleaned_data['password']
        if commit:
            model.save()
        return model


class ServiceAdmin(admin.ModelAdmin):
    def activate_active_flag(self, request, queryset):
        rows_updated = queryset.update(is_active=1)
        message = ungettext("1 service was successfully marked as active.",
                            "{rows_updated} services were successfully marked"
                            " as active.",
                            rows_updated).format(rows_updated=rows_updated)
        self.message_user(request, message)

    activate_active_flag.short_description = _("Activate")

    def deactivate_active_flag(self, request, queryset):
        rows_updated = queryset.update(is_active=0)
        message = ungettext("1 service was successfully marked as inactive.",
                            "{rows_updated} services were successfully marked"
                            " as inactive.",
                            rows_updated).format(rows_updated=rows_updated)
        self.message_user(
            request,
            message
        )

    deactivate_active_flag.short_description = _("Deactivate")

    def activate_core_services_flag(self, request, queryset):
        rows_updated = queryset.update(is_core_service=1)
        message = ungettext("1 service was successfully marked as core.",
                            "{rows_updated} services were successfully marked"
                            " as core.",
                            rows_updated).format(rows_updated=rows_updated)
        self.message_user(
            request,
            message
        )

    activate_core_services_flag.short_description = _("Mark as core")

    def deactivate_core_services_flag(self, request, queryset):
        rows_updated = queryset.update(is_core_service=0)
        message = ungettext("1 service was successfully marked as not core.",
                     "{rows_updated} services were successfully marked as"
                     " not core.",
                     rows_updated).format(rows_updated=rows_updated)
        self.message_user(
            request,
            message
        )

    deactivate_core_services_flag.short_description = _("Mark as not core")

    def activate_technical_break_flag(self, request, queryset):
        rows_updated = queryset.update(is_technical_break=1)
        message = ungettext("1 service was successfully switched to technical"
                            " break state.",
                            "{rows_updated} services were successfully"
                            " switched to technical break state.",
                            rows_updated).format(rows_updated=rows_updated)
        self.message_user(
            request,
            message
        )

    activate_technical_break_flag.short_description = \
        _("Switch to technical break state")

    def deactivate_technical_break_flag(self, request, queryset):
        rows_updated = queryset.update(is_technical_break=0)
        message = ungettext("1 service was successfully switched to"
                            " active state.",
                            "{rows_updated} services were successfully"
                            " switched to active state.",
                            rows_updated).format(rows_updated=rows_updated)
        self.message_user(
            request,
            message
        )

    deactivate_technical_break_flag.short_description = \
        _("Disable technical break state")

    def activate_hosting_flag(self, request, queryset):
        rows_updated = queryset.update(hosting=1)
        message = ungettext("1 service was successfully marked as hosting.",
                            "{rows_updated} services were successfully marked"
                            " as hosting.",
                            rows_updated).format(rows_updated=rows_updated)
        self.message_user(
            request,
            message
        )

    activate_hosting_flag.short_description = _("Mark as hosting")

    def deactivate_hosting_flag(self, request, queryset):
        rows_updated = queryset.update(hosting=0)
        message = ungettext(
            "1 service was successfully marked as not hosting.",
            "{rows_updated} services were successfully marked as"
            " not hosting.",
            rows_updated).format(rows_updated=rows_updated)
        self.message_user(
            request,
            message
        )

    deactivate_hosting_flag.short_description = _("Mark as not hosting")

    form = ServiceAdminForm
    fieldsets = [
        (None, {'fields': ['name', 'url', 'response_code', 'is_active',
                           'is_core_service', 'is_technical_break',
                           'hosting', 'comments', 'order']}),
        (_('Params'), {'fields': ['sensitivity',
                                  'performance_issues_time',
                                  'connection_timeout',
                                  'service_working_min_probes_count',
                                  'time_delta',
                                  'base_useragent',
                                  'base_referer']}),
        (_('Integration'), {'fields': ['maas_intkey', 'sc_id']}),
        (_('Additional agents'), {'fields': ['additional_agents']}),
        (_('Authentication'), {'fields': ['auth_method', 'user', 'password']}),
    ]
    fields = ()
    list_display = (
        'name', 'url', 'is_active', 'is_core_service', 'is_technical_break',
        'hosting', 'sensitivity', 'auth_method', 'created', 'modified',
    )
    list_per_page = settings.DEFAULT_LIST_ITEMS_PER_PAGE
    inlines = [MonitoredPhrasesInLine, AdditionalRequestParamInLine]
    list_filter = (
        'is_active', 'is_core_service', 'is_technical_break', 'hosting',
        'auth_method',
    )
    search_fields = ['name', ]
    filter_horizontal = ('additional_agents',)
    actions = [
        activate_active_flag,
        deactivate_active_flag,
        activate_core_services_flag,
        deactivate_core_services_flag,
        activate_technical_break_flag,
        deactivate_technical_break_flag,
        activate_hosting_flag,
        deactivate_hosting_flag,
    ]

admin.site.register(Service, ServiceAdmin)


class AgentAdminForm(forms.ModelForm):
    class Meta:
        model = Agent

    def clean(self):
        cleaned_data = super(AgentAdminForm, self).clean()
        is_main = cleaned_data.get("is_main")
        is_active = cleaned_data.get("is_active")
        if is_main and not is_active:
            msg = _("Inactive agent can not be set as the main.")
            self._errors["is_main"] = self.error_class([msg])
        return cleaned_data


class QueueAdmin(admin.ModelAdmin):
    pass

admin.site.register(Queue, QueueAdmin)


class AgentAdmin(admin.ModelAdmin):
    fields = ('name', 'queue', 'is_main', 'is_active')
    list_display = ('name', 'queue', 'salt', 'is_main', 'is_active')
    list_per_page = settings.DEFAULT_LIST_ITEMS_PER_PAGE
    list_filter = ('is_main',)
    search_fields = ['name', ]
    form = AgentAdminForm

    def save_model(self, request, obj, form, change):
        obj.save()
        if obj.is_main:
            Agent.objects.exclude(
                pk=obj.pk,
            ).filter(
                is_main=True,
            ).update(
                is_main=False,
            )

admin.site.register(Agent, AgentAdmin)
