# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables

from manila_ui.dashboards.project.shares import tables as shares_tables
from manila_ui import features


class MigrationStartAction(tables.LinkAction):
    name = "migration_start"
    verbose_name = _("Migrate Share")
    url = "horizon:admin:shares:migration_start"
    classes = ("ajax-modal",)
    policy_rules = (("share", "migration_start"),)
    ajax = True

    def allowed(self, request, share=None):
        if share:
            return (share.status.upper() == "AVAILABLE" and
                    not getattr(share, 'has_snapshot', False) and
                    features.is_migration_enabled())
        return False


class MigrationCompleteAction(tables.LinkAction):
    name = "migration_complete"
    verbose_name = _("Complete migration")
    url = "horizon:admin:shares:migration_complete"
    classes = ("ajax-modal",)
    policy_rules = (("share", "migration_complete"),)
    ajax = True

    def allowed(self, request, share=None):
        if (share and share.status.upper() == "MIGRATING" and
                features.is_migration_enabled()):
            return True
        return False


class MigrationCancelAction(tables.LinkAction):
    name = "migration_cancel"
    verbose_name = _("Cancel migration")
    url = "horizon:admin:shares:migration_cancel"
    classes = ("ajax-modal",)
    policy_rules = (("share", "migration_cancel"),)
    ajax = True

    def allowed(self, request, share=None):
        if (share and share.status.upper() == "MIGRATING" and
                features.is_migration_enabled()):
            return True
        return False


class MigrationGetProgressAction(tables.LinkAction):
    name = "migration_get_progress"
    verbose_name = _("Get migration progress")
    url = "horizon:admin:shares:migration_get_progress"
    classes = ("ajax-modal",)
    policy_rules = (("share", "migration_get_progress"),)
    ajax = True

    def allowed(self, request, share=None):
        if (share and share.status.upper() == "MIGRATING" and
                features.is_migration_enabled()):
            return True
        return False


class ManageShareAction(tables.LinkAction):
    name = "manage"
    verbose_name = _("Manage Share")
    url = "horizon:admin:shares:manage"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("share", "share_extension:share_manage"),)
    ajax = True


class UnmanageShareAction(tables.LinkAction):
    name = "unmanage"
    verbose_name = _("Unmanage Share")
    url = "horizon:admin:shares:unmanage"
    classes = ("ajax-modal",)
    icon = "pencil"
    policy_rules = (("share", "share_extension:share_unmanage"),)

    def allowed(self, request, share=None):
        if (not share or share.share_server_id or
                share.status.upper() not in shares_tables.DELETABLE_STATES):
            return False
        elif hasattr(share, 'has_snapshot'):
            return not share.has_snapshot
        return False


class ManageReplicas(tables.LinkAction):
    name = "manage_replicas"
    verbose_name = _("Manage Replicas")
    url = "horizon:admin:shares:manage_replicas"
    classes = ("btn-edit",)
    policy_rules = (("share", "share:replica_get_all"),)

    def allowed(self, request, share):
        share_replication_enabled = share.replication_type is not None
        return features.is_replication_enabled() and share_replication_enabled


class SharesTable(shares_tables.SharesTable):
    name = tables.WrappingColumn(
        "name", verbose_name=_("Name"),
        link="horizon:admin:shares:detail")
    host = tables.Column("host", verbose_name=_("Host"))
    project = tables.Column("project_name", verbose_name=_("Project"))

    def get_share_server_link(share):
        if getattr(share, 'share_server_id', None):
            return reverse("horizon:admin:share_servers:share_server_detail",
                           args=(share.share_server_id,))
        else:
            return None

    share_server = tables.Column(
        "share_server_id",
        verbose_name=_("Share Server"),
        link=get_share_server_link)

    class Meta(object):
        name = "shares"
        verbose_name = _("Shares")
        status_columns = ["status"]
        row_class = shares_tables.UpdateRow
        table_actions = (
            tables.NameFilterAction,
            ManageShareAction,
            shares_tables.DeleteShare,
        )
        row_actions = (
            ManageReplicas,
            MigrationStartAction,
            MigrationCompleteAction,
            MigrationGetProgressAction,
            MigrationCancelAction,
            UnmanageShareAction,
            shares_tables.DeleteShare,
        )
        columns = [
            'tenant', 'host', 'name', 'size', 'status', 'visibility',
            'share_type', 'protocol', 'share_server',
        ]
        if features.is_share_groups_enabled():
            columns.append('share_group_id')
