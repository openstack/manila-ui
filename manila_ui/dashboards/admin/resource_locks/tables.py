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

import uuid

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from horizon import tables

from manila_ui.dashboards.project.resource_locks import (
    tables as project_tables)


class AdminEditLock(project_tables.EditLock):
    url = "horizon:admin:resource_locks:update"


def get_admin_share_link(lock):
    return reverse("horizon:admin:shares:detail", args=(lock.resource_id,))


def get_admin_rule_link(lock):
    parent_id = getattr(lock, 'parent_resource_id', None)
    try:
        uuid.UUID(parent_id)
        return reverse("horizon:admin:shares:detail", args=(parent_id,))
    except (ValueError, TypeError, AttributeError):
        return None


class SharesLockTable(project_tables.SharesLockTable):
    resource_name = tables.Column(
        "resource_name",
        verbose_name=_("Share Name"),
        link=get_admin_share_link)

    class Meta(project_tables.SharesLockTable.Meta):
        row_actions = (AdminEditLock, project_tables.DeleteLock)


class AccessRulesLockTable(project_tables.AccessRulesLockTable):
    parent_share = tables.Column(
        "parent_resource_name",
        verbose_name=_("Parent Share"),
        link=get_admin_rule_link)

    class Meta(project_tables.AccessRulesLockTable.Meta):
        row_actions = (AdminEditLock, project_tables.DeleteLock)
