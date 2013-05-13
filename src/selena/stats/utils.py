#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from services.models import ResponseStateChoices as RSC


def get_real_problems_number(items, die_services_mode=False,
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
    for key in groups:
        all_probes_with_err = True
        for probe in groups[key]:
            if die_services_mode:
                if any((
                    probe.response_state == RSC.ok.id,
                    probe.response_state == RSC.performance.id,
                    probe.response_state == RSC.wordcheck_error.id,
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
        if all_probes_with_err:
            i += 1
            all_probes_failed_groups.append(key)
    if not get_first_and_last_broken_probes:
        return i
    first_broken_probe = None
    last_broken_probe = None
    if i > 0:
        first_broken_probe = groups[sorted(all_probes_failed_groups)[0]][0]
        last_broken_probe = groups[sorted(all_probes_failed_groups)[-1]][0]
    return {
        'real_problems_number': i,
        'first_broken_probe': first_broken_probe,
        'last_broken_probe': last_broken_probe,
    }
