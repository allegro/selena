#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from boards.views.boards import (
    CoreServices,
    CoreServicesErrorsOnly,
    CustomBoards,
    ErrorMessage,
    ErrorsOnly,
    Home,
    NotCoreServices,
    ProbeDetails,
    ServiceDetails,
)
from boards.views.charts import BarChart
from boards.views.reports import CSVErrorsReport, FullHistory
from stats.api.resources import IncidentResource, ServiceResource
from tastypie.api import Api


admin.autodiscover()


v01_api = Api(api_name='v0.1')
v01_api.register(IncidentResource())
v01_api.register(ServiceResource())


urlpatterns = patterns(
    '',
    url(r'^$', login_required(Home.as_view())),
    url(r'^mode/core-services$', login_required(CoreServices.as_view())),
    url(r'^mode/errors-only$', login_required(ErrorsOnly.as_view())),
    url(
        r'^mode/core-services-errors-only$',
        login_required(CoreServicesErrorsOnly.as_view()),
    ),
    url(
        r'^mode/non-core-services$',
        login_required(NotCoreServices.as_view()),
    ),
    url(
        r'^manually-defined/(?P<board_id>[0-9]+)$',
        login_required(CustomBoards.as_view()),
    ),
    url(
        r'^show/(?P<service_id>[0-9]+)$',
        login_required(ServiceDetails.as_view()),
    ),
    url(
        r'^get-bar-chart/(?P<service_id>[0-9]+)$',
        login_required(BarChart.as_view()),
    ),
    url(
        r'^get-probe-details/(?P<probe_id>[0-9]+)$',
        login_required(ProbeDetails.as_view()),
    ),
    url(
        r'^get-error-msg/(?P<probe_id>[0-9]+)$',
        login_required(ErrorMessage.as_view()),
    ),
    url(
        r'^history/(?P<service_id>[0-9]+)$',
        login_required(FullHistory.as_view()),
    ),
    url(r'^generate-errors-report', login_required(CSVErrorsReport.as_view())),

    url(r'^api/', include(v01_api.urls)),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
