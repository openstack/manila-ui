# Copyright (c) 2016 Mirantis, Inc.
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

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import messages
from horizon import tables

from manila_ui.api import manila
from manila_ui.dashboards.project.shares.replicas import (
    tables as replica_tables)


DELETABLE_STATUSES = ("error", "available")


class UpdateReplicaRow(tables.Row):
    ajax = True

    def get_data(self, request, replica_id):
        replica = manila.share_replica_get(request, replica_id)
        return replica


class ResyncReplica(tables.LinkAction):
    name = "resync_replica"
    verbose_name = _("Resync replica")
    url = "horizon:admin:shares:resync_replica"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share_replica", "share_replica:resync"),)

    def allowed(self, request, replica=None):
        return True

    def get_policy_target(self, request, datum=None):
        return {"project_id": getattr(datum, "project_id", None)}

    def get_link_url(self, replica):
        return reverse(self.url, args=(replica.id,))


class ResetReplicaState(tables.LinkAction):
    name = "reset_replica_state"
    verbose_name = _("Reset replica state")
    url = "horizon:admin:shares:reset_replica_state"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share_replica", "share_replica:reset_replica_state"),)

    def allowed(self, request, replica=None):
        return True

    def get_policy_target(self, request, datum=None):
        return {"project_id": getattr(datum, "project_id", None)}

    def get_link_url(self, replica):
        return reverse(self.url, args=(replica.id,))


class ResetReplicaStatus(tables.LinkAction):
    name = "reset_replica_status"
    verbose_name = _("Reset replica status")
    url = "horizon:admin:shares:reset_replica_status"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share_replica", "share_replica:reset_status"),)

    def allowed(self, request, replica=None):
        return True

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


_DETAIL_URL = "horizon:admin:shares:replica_detail"


class ReplicasTable(replica_tables.ReplicasTable):

    class Meta(object):
        name = "replicas"
        verbose_name = _("Replicas")
        status_columns = ("status",)
        row_class = UpdateReplicaRow
        row_actions = (
            ResyncReplica,
            ResetReplicaState,
            ResetReplicaStatus,
            DeleteReplica)
