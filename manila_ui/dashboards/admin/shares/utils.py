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

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from openstack_dashboard.api import keystone


def set_tenant_name_to_objects(request, objects):
    try:
        tenants, has_more = keystone.tenant_list(request)
    except Exception:
        tenants = []
        msg = _('Unable to retrieve share project information.')
        exceptions.handle(request, msg)

    tenant_dict = dict([(t.id, t) for t in tenants])
    for obj in objects:
        tenant_id = getattr(obj, "project_id", None)
        tenant = tenant_dict.get(tenant_id, None)
        obj.tenant_name = getattr(tenant, "name", None)
