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


from django.template.defaultfilters import title
from django.urls import reverse
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import exceptions
from horizon import tables

from manila_ui.api import manila
import manila_ui.dashboards.project.share_snapshots.tables as ss_tables
from manila_ui.dashboards.project.shares import tables as shares_tables


def get_size(share):
    return _("%sGiB") % share.size


class ShareSnapshotShareNameColumn(tables.Column):
    def get_link_url(self, snapshot):
        return reverse(self.link, args=(snapshot.share_id,))


class DeleteShareSnapshot(tables.DeleteAction):

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Snapshot",
            u"Delete Snapshots",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Snapshot",
            u"Deleted Snapshots",
            count
        )

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "project_id", None)
        return {"project_id": project_id}

    def delete(self, request, obj_id):
        obj = self.table.get_object_by_id(obj_id)
        name = self.table.get_object_display(obj)
        try:
            manila.share_snapshot_delete(request, obj_id)
        except Exception:
            msg = _('Unable to delete snapshot "%s". One or more shares '
                    'depend on it.')
            exceptions.check_message(["snapshots", "dependent"], msg % name)
            raise

    def allowed(self, request, snapshot=None):
        if snapshot:
            return snapshot.status.upper() in shares_tables.DELETABLE_STATES
        return True


class ShareSnapshotsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("in-use", True),
        ("available", True),
        ("creating", None),
        ("error", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("in-use", pgettext_lazy("Current status of snapshot", u"In-use")),
        ("available",
         pgettext_lazy("Current status of snapshot", u"Available")),
        ("creating", pgettext_lazy("Current status of snapshot", u"Creating")),
        ("error", pgettext_lazy("Current status of snapshot", u"Error")),
    )
    name = tables.WrappingColumn(
        "name", verbose_name=_("Name"),
        link="horizon:admin:share_snapshots:share_snapshot_detail")
    description = tables.Column(
        "description",
        verbose_name=_("Description"),
        truncate=40)
    size = tables.Column(
        get_size,
        verbose_name=_("Size"),
        attrs={'data-type': 'size'})
    status = tables.Column(
        "status",
        filters=(title,),
        verbose_name=_("Status"),
        status=True,
        status_choices=STATUS_CHOICES,
        display_choices=STATUS_DISPLAY_CHOICES)
    source = ShareSnapshotShareNameColumn(
        "share",
        verbose_name=_("Source"),
        link="horizon:admin:shares:detail")

    def get_object_display(self, obj):
        return obj.name

    class Meta(object):
        name = "share_snapshots"
        verbose_name = _("Share Snapshots")
        status_columns = ["status"]
        row_class = ss_tables.UpdateShareSnapshotRow
        table_actions = (
            tables.NameFilterAction,
            DeleteShareSnapshot,
        )
        row_actions = (
            DeleteShareSnapshot,
        )
