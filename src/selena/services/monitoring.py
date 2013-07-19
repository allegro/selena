#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import re
import time

from uuid import uuid4

import django_rq

from django.conf import settings
from django.core.cache import cache
from rq.exceptions import NoSuchJobError
from rq.job import Job
from selena_agent.monitor import run_test
from selena_agent.utils import create_token
from services.models import (
    Agent,
    ResponseStateChoices,
    ServiceHistory,
    ServiceHistoryExtra,
)


PREPARE_GET_REG = re.compile(r'.*\?[a-zA-Z0-9]+=.+')


class MainAgentDoesNotExist(Exception):
    pass


def _get_redis_connection(queue_name):
    return django_rq.queues.get_redis_connection(
        settings.RQ_QUEUES[queue_name],
    )


def _get_monitored_phrases(service):
    phrases = {}
    cached_phrases = {}
    for phrase in service.monitoredphrase_set.filter(is_active=True):
        phrases[phrase.id] = [phrase.phrase, phrase.shall_not_be]
        cached_phrases[phrase.id] = phrase.phrase
    return json.dumps(phrases), cached_phrases


def _prepare_get_data(get_params_string, url):
        if not get_params_string:
            return ''
        m = PREPARE_GET_REG.match(url)
        if m and url[-1] == "&":
            return get_params_string
        elif m:
            return "&%s" % get_params_string
        else:
            return "?%s" % get_params_string


def _get_main_agent():
    main_agent = cache.get('main_agent')
    if not main_agent:
        try:
            main_agent = Agent.objects.get(is_main=True, is_active=True)
            cache.set('main_agent', main_agent, 60)
        except Agent.DoesNotExist:
            return
    return main_agent


def _get_agent_by_id(agent_id):
    agent = cache.get('agent_%s' % agent_id)
    if not agent:
        try:
            agent = Agent.objects.get(id=agent_id, is_active=True)
            cache.set('agent_%s' % agent_id, agent, 60)
        except Agent.DoesNotExist:
            return
    return agent


def _get_test_cases(service, monitored_phrases=''):
    main_agent = _get_main_agent()
    if not main_agent:
        raise MainAgentDoesNotExist()
    cases = [{
        'url': service.url,
        'useragent': service.base_useragent,
        'agent_queue_name': main_agent.queue.name,
        'agent_id': main_agent.id,
        'referer': service.base_referer,
        'arp_id': None,
        'auth': {
            'method': service.auth_method,
            'user': service.user,
            'password': service.password,
        },
        'post': None,
        'monitored_phrases': monitored_phrases,
        'connection_timeout': service.connection_timeout,
        'response_code': service.response_code,
        'performance_issues_time': service.performance_issues_time,
        'connection_timeout': service.connection_timeout,
    }]
    params = service.additionalrequestparam_set.all()
    for param in params:
        cases.append({
            'url': '%s%s' % (
                service.url,
                _prepare_get_data(param.get, service.url),
            ),
            'useragent': param.useragent,
            'agent_queue_name': main_agent.queue.name,
            'agent_id': main_agent.id,
            'referer': param.referer,
            'arp_id': param.id,
            'auth': {
                'method': service.auth_method,
                'user': service.user,
                'password': service.password,
            },
            'post': param.post,
            'monitored_phrases': monitored_phrases,
            'connection_timeout': service.connection_timeout,
            'response_code': service.response_code,
            'performance_issues_time': service.performance_issues_time,
            'connection_timeout': service.connection_timeout,
        })
    for agent in service.additional_agents.filter(
        is_active=True,
    ).exclude(
        is_main=True,
    ):
        cases.append({
            'url': service.url,
            'useragent': service.base_useragent,
            'agent_queue_name': agent.queue.name,
            'agent_id': agent.id,
            'referer': service.base_referer,
            'arp_id': None,
            'auth': {
                'method': service.auth_method,
                'user': service.user,
                'password': service.password,
            },
            'post': None,
            'monitored_phrases': monitored_phrases,
            'connection_timeout': service.connection_timeout,
            'response_code': service.response_code,
            'performance_issues_time': service.performance_issues_time,
            'connection_timeout': service.connection_timeout,
        })
        for param in params:
            cases.append({
                'url': '%s%s' % (
                    service.url,
                    _prepare_get_data(param.get, service.url),
                ),
                'useragent': param.useragent,
                'agent_queue_name': agent.queue.name,
                'agent_id': agent.id,
                'referer': param.referer,
                'arp_id': param.id,
                'auth': {
                    'method': service.auth_method,
                    'user': service.user,
                    'password': service.password,
                },
                'post': param.post,
                'monitored_phrases': monitored_phrases,
                'connection_timeout': service.connection_timeout,
                'response_code': service.response_code,
                'performance_issues_time': service.performance_issues_time,
                'connection_timeout': service.connection_timeout,
            })
    return cases


def _test_service_summary(service_id, task_uuid, start_time, jobs, sensitivity,
                          results={}, cases={}, wordchecks={}):
    if (int(time.time()) - start_time) > 120:
        return
    for job_id, queue_name in jobs:
        if job_id in results:
            continue
        try:
            job = Job.fetch(
                job_id,
                connection=_get_redis_connection(queue_name),
            )
        except NoSuchJobError:
            results[job_id] = None
            continue
        if job.is_failed:
            results[job_id] = None
            job.delete()
        elif job.result is not None:
            results[job_id] = job.result
            job.delete()
        elif (int(time.time()) - start_time) > 105:
            results[job_id] = None
    if len(results) < len(jobs):
        queue = django_rq.get_queue(
            name='monitors' if 'monitors' in settings.RQ_QUEUES else 'default',
        )
        queue.enqueue_call(
            func=_test_service_summary,
            kwargs={
                'service_id': service_id,
                'task_uuid': task_uuid,
                'start_time': start_time,
                'jobs': jobs,
                'sensitivity': sensitivity,
                'results': results,
                'cases': cases,
                'wordchecks': wordchecks,
            },
            timeout=120,
            result_ttl=0,
        )
        return
    main_probe = None
    tick_cases_number = 0
    failed_cases_number = 0
    for job_id, result in results.items():
        if not result:
            result = {
                'response_state': ResponseStateChoices.agent_failed,
                'response_time': 0,
                'response_code': 0,
            }
        agent = _get_agent_by_id(cases[job_id]['agent_id'])
        if not agent:
            continue
        token = result.get('token')
        if all((
            token != create_token(result, task_uuid, agent.salt),
            result.get('response_state') != ResponseStateChoices.agent_failed,
        )):
            continue
        tick_cases_number += 1
        sh = ServiceHistory(
            service_id=service_id,
            response_state=result.get('response_state'),
            response_code=result.get('response_code'),
            response_time=result.get('response_time'),
            namelookup_time=result.get('namelookup_time'),
            connect_time=result.get('connect_time'),
            pretransfer_time=result.get('pretransfer_time'),
            starttransfer_time=result.get('starttransfer_time'),
            redirect_time=result.get('redirect_time'),
            size_download=result.get('size_download'),
            speed_download=result.get('speed_download'),
            redirect_count=result.get('redirect_count'),
            num_connects=result.get('num_connects'),
            agent_id=cases[job_id]['agent_id'],
        )
        if cases[job_id]['arp_id']:
            sh.request_params_id = cases[job_id]['arp_id']
        wordchecks_errors = []
        if 'monitored_phrases' in result and result['monitored_phrases']:
            for wordcheck_id in wordchecks:
                try:
                    if not result['monitored_phrases'][str(wordcheck_id)]:
                        wordchecks_errors.append(wordchecks[wordcheck_id])
                except KeyError:
                    continue
            wordchecks_errors = ", ".join(wordchecks_errors)
            if all((
                sh.response_state == ResponseStateChoices.ok,
                wordchecks_errors,
            )):
                sh.response_state = ResponseStateChoices.wordcheck_error
        if sh.response_state != ResponseStateChoices.ok:
            failed_cases_number += 1
        if main_probe:
            sh.main_probe = main_probe.id
        sh.save()
        if not main_probe:
            main_probe = sh
        effective_url = result.get('effective_url', '')
        service_url = cases[job_id]['url']
        try:
            if effective_url[-1] == "/":
                effective_url = effective_url[0:-1]
            if service_url[-1] == "/":
                service_url = service_url[0:-1]
        except IndexError:
            pass
        extra = None
        if effective_url and service_url != effective_url:
            extra = ServiceHistoryExtra(service_history_id=sh.pk)
            extra.effective_url = effective_url
        error = result.get('error')
        if error:
            if extra is None:
                extra = ServiceHistoryExtra(service_history_id=sh.pk)
            extra.error_msg = error
        if wordchecks_errors:
            if extra is None:
                extra = ServiceHistoryExtra(service_history_id=sh.pk)
            extra.wordchecks_errors = wordchecks_errors
        if extra is not None:
            extra.save()
    if max(int(sensitivity * tick_cases_number), 1) <= failed_cases_number:
        main_probe.tick_failed = True
        main_probe.save()


def test_service(service):
    task_uuid = str(uuid4())
    monitored_phrases, cached_wordchecks = _get_monitored_phrases(service)
    cases = _get_test_cases(service, monitored_phrases)
    start_time = int(time.time())
    cases_cache = {}
    jobs = []
    for case in cases:
        agent_queue = django_rq.get_queue(case['agent_queue_name'])
        case.update({'uuid': task_uuid})
        job = agent_queue.enqueue_call(
            func=run_test,
            kwargs={'config': case, 'start_time': start_time},
            timeout=45,
            result_ttl=180,
        )
        jobs.append((job.id, case['agent_queue_name']))
        cases_cache[job.id] = case
    queue = django_rq.get_queue(
        name='monitors' if 'monitors' in settings.RQ_QUEUES else 'default',
    )
    queue.enqueue_call(
        func=_test_service_summary,
        kwargs={
            'service_id': service.id,
            'task_uuid': task_uuid,
            'start_time': start_time,
            'jobs': jobs,
            'sensitivity': service.sensitivity,
            'cases': cases_cache,
            'wordchecks': cached_wordchecks,
        },
        timeout=45,
        result_ttl=0,
    )
