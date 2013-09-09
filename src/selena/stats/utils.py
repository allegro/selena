#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from services.models import ResponseStateChoices as RSC


def get_real_problems_number(items, ok_mode=False,
                             get_first_and_last_broken_probes=False):
    groups = {}
    for probe in items:
        if probe.main_probe == 0:
            group_id = probe.id
        else:
            group_id = probe.main_probe
        if group_id not in groups:
            groups[group_id] = []
        groups[group_id].append(probe)
    all_probes_failed_groups = []
    i = 0
    nr_of_failure_probes = 0
    nr_of_performance_probes = 0
    problem_type = None
    for key in groups:
        all_probes_with_err = True
        all_probes_with_agent_failed = True
        for probe in groups[key]:
            if probe.response_state != RSC.agent_failed.id:
                all_probes_with_agent_failed = False
            if ok_mode:
                if any((
                    probe.response_state == RSC.die.id,
                    probe.response_state == RSC.performance.id,
                )):
                    all_probes_with_err = False
                    break
            else:
                if any((
                    probe.response_state == RSC.ok.id,
                    probe.response_state == RSC.wordcheck_error.id,
                )):
                    all_probes_with_err = False
                    break
            if probe.response_state == RSC.die.id:
                nr_of_failure_probes += 1
            elif probe.response_state == RSC.performance.id:
                nr_of_performance_probes += 1
        if ((all_probes_with_err and all_probes_with_agent_failed is False) or
                (ok_mode and all_probes_with_agent_failed)):
            i += 1
            all_probes_failed_groups.append(key)

    if nr_of_performance_probes <= nr_of_failure_probes:
        problem_type = 'failure'
    else:
        problem_type = 'performance'

    if not get_first_and_last_broken_probes:
        return {
            'real_problems_number': i,
            'problem_type': problem_type,
        }
    first_broken_probe = None
    last_broken_probe = None
    if i > 0:
        first_broken_probe = groups[sorted(all_probes_failed_groups)[0]][0]
        last_broken_probe = groups[sorted(all_probes_failed_groups)[-1]][0]
    return {
        'problem_type': problem_type,
        'real_problems_number': i,
        'first_broken_probe': first_broken_probe,
        'last_broken_probe': last_broken_probe,
    }
