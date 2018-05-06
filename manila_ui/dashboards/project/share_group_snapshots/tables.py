# Copyright 2017 Mirantis, Inc.
# All rights reserved.
#
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
from django.utils.http import urlencode
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import exceptions
from horizon import tables
from horizon.utils import filters

from manila_ui.api import manila


class UpdateShareGroupSnapshot(tables.LinkAction):
    name = "update_share_group_snapshot"
    verbose_name = _("Update")
    url = "horizon:project:share_group_snapshots:update"
    classes = ("ajax-modal", "btn-camera")

    def allowed(self, request, share_group_snapshot=None):
        return share_group_snapshot.status in ("available", "error")


class CreateShareGroupSnapshot(tables.LinkAction):
    name = "create_share_group_snapshot"
    verbose_name = _("Create Share Group Snapshot")
    url = "horizon:project:share_group_snapshots:create"
    classes = ("ajax-modal", "btn-camera")

    def allowed(self, request, share_group=None):
        self.verbose_name = _("Create Share Group Snapshot")
        classes = [c for c in self.classes if c != "disabled"]
        self.classes = classes
        return share_group.status == "available"


class CreateShareGroupFromSnapshot(tables.LinkAction):
    name = "create_share_group_from_snapshot"
    verbose_name = _("Create Share Group")
    url = "horizon:project:share_groups:create"
    classes = ("ajax-modal", "btn-camera")

    def get_link_url(self, datum):
        base_url = reverse(self.url)
        params = urlencode({
            "snapshot_id": self.table.get_object_id(datum)})
        return "?".join([base_url, params])

    def allowed(self, request, share_group=None):
        return share_group.status == "available"


class ShareGroupSnapshotShareGroupNameColumn(tables.Column):
    def get_link_url(self, snapshot):
        return reverse(self.link, args=(snapshot.share_group_id,))


class DeleteShareGroupSnapshot(tables.DeleteAction):

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Share Group Snapshot",
            u"Delete Share Group Snapshots",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Share Group Snapshot",
            u"Deleted Share Group Snapshots",
            count
        )

    def delete(self, request, obj_id):
        obj = self.table.get_object_by_id(obj_id)
        name = self.table.get_object_display(obj)
        try:
            manila.share_group_snapshot_delete(request, obj_id)
        except Exception:
            msg = _('Unable to delete share group snapshot "%s". '
                    'One or more share groups depend on it.')
            exceptions.check_message(["snapshots", "dependent"], msg % name)
            raise

    def allowed(self, request, snapshot=None):
        if snapshot:
            return snapshot.status.lower() in ('available', 'error')
        return True


class UpdateShareGroupSnapshotRow(tables.Row):
    ajax = True

    def get_data(self, request, share_group_snapshot_id):
        snapshot = manila.share_group_snapshot_get(
            request, share_group_snapshot_id)
        if not snapshot.name:
            snapshot.name = share_group_snapshot_id
        return snapshot


class ShareGroupSnapshotsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("available", True),
        ("creating", None),
        ("error", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("available",
         pgettext_lazy("Current status of snapshot", u"Available")),
        ("creating", pgettext_lazy("Current status of snapshot", u"Creating")),
        ("error", pgettext_lazy("Current status of snapshot", u"Error")),
    )
    name = tables.WrappingColumn(
        "name", verbose_name=_("Name"),
        link="horizon:project:share_group_snapshots:detail")
    description = tables.Column(
        "description",
        verbose_name=_("Description"),
        truncate=40)
    created_at = tables.Column(
        "created_at",
        verbose_name=_("Created at"),
        filters=(
            filters.parse_isotime,
        ))
    status = tables.Column(
        "status",
        filters=(title,),
        verbose_name=_("Status"),
        status=True,
        status_choices=STATUS_CHOICES,
        display_choices=STATUS_DISPLAY_CHOICES)
    source = ShareGroupSnapshotShareGroupNameColumn(
        "share_group",
        verbose_name=_("Source"),
        link="horizon:project:share_groups:detail")

    def get_object_display(self, obj):
        return obj.name

    class Meta(object):
        name = "share_group_snapshots"
        verbose_name = _("Share Group Snapshots")
        status_columns = ["status"]
        row_class = UpdateShareGroupSnapshotRow
        table_actions = (
            tables.NameFilterAction,
            DeleteShareGroupSnapshot,
        )
        row_actions = (
            CreateShareGroupFromSnapshot,
            UpdateShareGroupSnapshot,
            DeleteShareGroupSnapshot,
        )
