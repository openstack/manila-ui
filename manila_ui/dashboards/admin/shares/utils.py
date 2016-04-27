# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_utils import timeutils

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from openstack_dashboard.api import keystone

PROJECTS = {}
TIME = None


def set_project_name_to_objects(request, objects):
    global PROJECTS, TIME
    try:
        # NOTE(vponomaryov): we will use saved values making lots of requests
        # in short period of time. 'memoized' is not suitable here
        now = timeutils.now()
        if TIME is None:
            TIME = now
        if not PROJECTS or now > TIME + 20:
            projects, has_more = keystone.tenant_list(request)
            PROJECTS = {t.id: t for t in projects}
            TIME = now
    except Exception:
        msg = _('Unable to retrieve list of projects.')
        exceptions.handle(request, msg)

    for obj in objects:
        project_id = getattr(obj, "project_id", None)
        project = PROJECTS.get(project_id, None)
        obj.project_name = getattr(project, "name", None)
