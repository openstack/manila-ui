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
from django.utils.translation import ngettext_lazy
from horizon import tables

from manila_ui.api import manila


class DeleteLock(tables.DeleteAction):
    policy_rules = (("share", "resource_lock:delete"),)

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            "Delete Lock", "Delete Locks", count)

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            "Deleted Lock", "Deleted Locks", count)

    def delete(self, request, obj_id):
        manila.resource_lock_delete(request, obj_id)


class EditLock(tables.LinkAction):
    name = "edit_lock"
    verbose_name = _("Edit Lock")
    url = "horizon:project:resource_locks:update"
    classes = ("ajax-modal",)
    icon = "pencil"
    policy_rules = (("share", "resource_lock:update"),)


def get_share_link(lock):
    return reverse("horizon:project:shares:detail", args=(lock.resource_id,))


def get_rule_link(lock):
    parent_id = getattr(lock, 'parent_resource_id', None)
    try:
        uuid.UUID(parent_id)
        return reverse("horizon:project:shares:detail", args=(parent_id,))
    except (ValueError, TypeError, AttributeError):
        return None


class ResourceLockFilterAction(tables.FilterAction):
    filter_type = "query"


class SharesLockTable(tables.DataTable):
    resource_name = tables.Column(
        "resource_name",
        verbose_name=_("Share Name"),
        link=get_share_link)
    user = tables.Column("user_name", verbose_name=_("User"))
    resource_action = tables.Column(
        "resource_action", verbose_name=_("Resource Action"))
    lock_reason = tables.Column("lock_reason", verbose_name=_("Lock Reason"))

    def get_object_display(self, obj):
        return getattr(obj, 'resource_name', None) or obj.id

    class Meta(object):
        name = "shares_locks"
        verbose_name = _("Locked Shares")
        table_actions = (tables.FilterAction,)
        row_actions = (EditLock, DeleteLock)


class AccessRulesLockTable(tables.DataTable):
    access_to = tables.Column("access_to", verbose_name=_("Access To"))
    parent_share = tables.Column(
        "parent_resource_name",
        verbose_name=_("Parent Share"),
        link=get_rule_link)
    user = tables.Column("user_name", verbose_name=_("User"))
    resource_action = tables.Column(
        "resource_action", verbose_name=_("Resource Action"))
    lock_reason = tables.Column("lock_reason", verbose_name=_("Lock Reason"))

    def get_object_display(self, obj):
        return getattr(obj, 'access_to', None) or obj.id

    class Meta(object):
        name = "rules_locks"
        verbose_name = _("Locked Access Rules")
        table_actions = (ResourceLockFilterAction,)
        row_actions = (EditLock, DeleteLock)
