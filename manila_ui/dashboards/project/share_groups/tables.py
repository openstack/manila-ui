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

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from horizon import tables

from manila_ui.api import manila
import manila_ui.dashboards.project.share_group_snapshots.tables as sgs_tables


class UpdateShareGroup(tables.LinkAction):
    name = "update"
    verbose_name = _("Update")
    url = "horizon:project:share_groups:update"
    classes = ("ajax-modal", "btn-create")

    def allowed(self, request, share_group=None):
        return share_group.status in ("available", "error")


class DeleteShareGroup(tables.DeleteAction):

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            u"Delete Share Group",
            u"Delete Share Groups",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            u"Deleted Share Group",
            u"Deleted Share Groups",
            count
        )

    def delete(self, request, obj_id):
        manila.share_group_delete(request, obj_id)

    def allowed(self, request, share_group=None):
        if share_group:
            # Row button
            return (share_group.status.lower() in ('available', 'error'))
        # Table button. Always return 'True'
        return True


class CreateShareGroup(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Share Group")
    url = "horizon:project:share_groups:create"
    classes = ("ajax-modal", "btn-create")
    icon = "plus"
    policy_rules = (("share", "share_group:create"),)

    def allowed(self, request, share=None):
        # TODO(vponomaryov): implement quota restriction when quota support
        # is implemented for share groups.
        # https://bugs.launchpad.net/manila/+bug/1868644
        return True


class UpdateShareGroupRow(tables.Row):
    ajax = True

    def get_data(self, request, sg_id):
        sg = manila.share_group_get(request, sg_id)
        return sg


class ShareGroupsTable(tables.DataTable):
    def get_share_network_link(share_group):
        if getattr(share_group, 'share_network_id', None):
            return reverse(
                "horizon:project:share_networks:share_network_detail",
                args=(share_group.share_network_id,))
        else:
            return None

    def get_source_share_group_snapshot_link(share_group):
        if getattr(share_group, 'source_share_group_snapshot_id', None):
            return reverse(
                "horizon:project:share_group_snapshots:detail",
                args=(share_group.source_share_group_snapshot_id,))
        else:
            return None

    STATUS_CHOICES = (
        ("available", True),
        ("creating", None),
        ("deleting", None),
        ("error", False),
        ("error_deleting", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("available", u"Available"),
        ("creating", u"Creating"),
        ("deleting", u"Deleting"),
        ("error", u"Error"),
        ("error_deleting", u"Error deleting"),
    )
    name = tables.Column(
        "name",
        verbose_name=_("Name"),
        link="horizon:project:share_groups:detail")
    status = tables.Column(
        "status",
        verbose_name=_("Status"),
        status=True,
        status_choices=STATUS_CHOICES,
        display_choices=STATUS_DISPLAY_CHOICES,
    )
    availability_zone = tables.Column(
        "availability_zone",
        verbose_name=_("Availability Zone"))
    share_network_id = tables.Column(
        "share_network_id",
        verbose_name=_("Share Network"),
        link=get_share_network_link)
    source_share_group_snapshot_id = tables.Column(
        "source_share_group_snapshot_id",
        verbose_name=_("Source Share Group Snapshot"),
        link=get_source_share_group_snapshot_link)

    def get_object_display(self, share_group):
        return str(share_group.id)

    def get_object_id(self, share_group):
        return str(share_group.id)

    class Meta(object):
        name = "share_groups"
        verbose_name = _("Share Groups")
        status_columns = ("status", )
        row_class = UpdateShareGroupRow
        table_actions = (
            CreateShareGroup,
            tables.NameFilterAction,
            DeleteShareGroup,
        )
        row_actions = (
            sgs_tables.CreateShareGroupSnapshot,
            UpdateShareGroup,
            DeleteShareGroup,
        )
