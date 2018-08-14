# Copyright (c) 2015 Mirantis, Inc.
# All rights reserved.
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

from django.template.defaultfilters import title
from django.urls import reverse
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
import six

from horizon import messages
from horizon import tables
from horizon.utils import filters

from manila_ui.api import manila


DELETABLE_STATUSES = ("error", "available")


class UpdateReplicaRow(tables.Row):
    ajax = True

    def get_data(self, request, replica_id):
        replica = manila.share_replica_get(request, replica_id)
        return replica


class CreateReplica(tables.LinkAction):
    name = "replicas"
    verbose_name = _("Create Replica")
    url = "horizon:project:shares:create_replica"
    classes = ("ajax-modal", "btn-camera")
    icon = "plus"
    policy_rules = (("share", "share:create_replica"),)

    def allowed(self, request, datum=None):
        share = manila.share_get(request, self.table.kwargs['share_id'])
        return share.replication_type is not None

    def get_policy_target(self, request, datum=None):
        return {"project_id": getattr(datum, "project_id", None)}

    def get_link_url(self):
        return reverse(self.url, args=[self.table.kwargs['share_id']])


class SetReplicaAsActive(tables.LinkAction):
    name = "set_replica_as_active"
    verbose_name = _("Set as Active")
    url = "horizon:project:shares:set_replica_as_active"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share_replica", "share_replica:promote"),)

    def allowed(self, request, replica=None):
        return replica.replica_state == "in_sync"

    def get_policy_target(self, request, datum=None):
        return {"project_id": getattr(datum, "project_id", None)}

    def get_link_url(self, replica):
        return reverse(self.url, args=(replica.id,))


class DeleteReplica(tables.DeleteAction):
    policy_rules = (("share_replica", "share_replica:delete"),)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Replica",
            u"Delete Replicas",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Replica",
            u"Deleted Replicas",
            count
        )

    def get_policy_target(self, request, datum=None):
        return {"project_id": getattr(datum, "project_id", None)}

    def delete(self, request, obj_id):
        try:
            manila.share_replica_delete(request, obj_id)
        except Exception:
            msg = _('Unable to delete replica "%s".') % obj_id
            messages.error(request, msg)

    def allowed(self, request, replica=None):
        if replica:
            share = manila.share_get(request, replica.share_id)
            replicas = manila.share_replica_list(request, replica.share_id)
            if share.replication_type is None:
                return False
            elif (share.replication_type is 'writable' and
                  replica.status in DELETABLE_STATUSES and
                  len(replicas) > 1) or (
                      share.replication_type in ('dr', 'readable') and
                      replica.status in DELETABLE_STATUSES and
                      replica.replica_state != 'active'):
                return True
        return False

    def single(self, data_table, request, object_id):
        try:
            manila.share_replica_delete(request, object_id)
            messages.success(
                request, _('Share replica %s has been deleted.') % object_id)
        except Exception:
            msg = _('Unable to delete replica "%s".') % object_id
            messages.error(request, msg)


_DETAIL_URL = "horizon:project:shares:replica_detail"


class ReplicasTable(tables.DataTable):
    STATUS_CHOICES = (
        ("creating", None),
        ("available", True),
        ("error", False),
        ("deleting", None),
    )
    STATUS_DISPLAY_CHOICES = (
        ("available",
         pgettext_lazy("Current status of replica", u"Available")),
        ("creating", pgettext_lazy("Current status of replica", u"Creating")),
        ("deleting", pgettext_lazy("Current status of replica", u"Deleting")),
        ("error", pgettext_lazy("Current status of replica", u"Error")),
    )
    id = tables.Column(
        "id",
        verbose_name=_("ID"),
        link=_DETAIL_URL,
    )

    availability_zone = tables.Column(
        "availability_zone", verbose_name=_("Availability zone"))

    status = tables.Column(
        "status",
        filters=(title,),
        verbose_name=_("Status"),
        status=True,
        status_choices=STATUS_CHOICES,
        display_choices=STATUS_DISPLAY_CHOICES,
    )

    replica_state = tables.Column(
        "replica_state", verbose_name=_("Replica State"))
    created_at = tables.Column(
        "created_at", verbose_name=_("Created At"),
        filters=(filters.parse_isotime,))
    updated_at = tables.Column(
        "updated_at", verbose_name=_("Updated At"),
        filters=(filters.parse_isotime,))

    def get_object_display(self, obj):
        return obj.id

    def get_object_id(self, obj):
        return six.text_type(obj.id)

    class Meta(object):
        name = "replicas"
        verbose_name = _("Replicas")
        status_columns = ("status",)
        row_class = UpdateReplicaRow
        table_actions = (
            CreateReplica,
        )
        row_actions = (
            SetReplicaAsActive,
            DeleteReplica)
