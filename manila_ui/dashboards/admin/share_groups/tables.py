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
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables
import six

from manila_ui.api import manila


class DeleteShareGroup(tables.DeleteAction):

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Share Group",
            u"Delete Share Groups",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Share Group",
            u"Deleted Share Groups",
            count
        )

    def delete(self, request, obj_id):
        manila.share_group_delete(request, obj_id)


class ResetShareGroupStatus(tables.LinkAction):
    name = "reset_share_group_status"
    verbose_name = _("Reset status")
    url = "horizon:admin:share_groups:reset_status"
    classes = ("ajax-modal", "btn-create")

    def allowed(self, request, share_group=None):
        return True


class ShareGroupsTable(tables.DataTable):
    def get_share_network_link(share_group):
        if getattr(share_group, 'share_network_id', None):
            return reverse("horizon:admin:share_networks:share_network_detail",
                           args=(share_group.share_network_id,))
        else:
            return None

    def get_share_server_link(share_group):
        if getattr(share_group, 'share_server_id', None):
            return reverse("horizon:admin:share_servers:share_server_detail",
                           args=(share_group.share_server_id,))
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
        link="horizon:admin:share_groups:detail")
    host = tables.Column("host", verbose_name=_("Host"))
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
    share_server_id = tables.Column(
        "share_server_id",
        verbose_name=_("Share Server"),
        link=get_share_server_link)

    def get_object_display(self, share_group):
        return six.text_type(share_group.id)

    def get_object_id(self, share_group):
        return six.text_type(share_group.id)

    class Meta(object):
        name = "share_groups"
        verbose_name = _("Share Groups")
        status_columns = ("status", )
        table_actions = (
            tables.NameFilterAction,
            DeleteShareGroup,
        )
        row_actions = (
            ResetShareGroupStatus,
            DeleteShareGroup,
        )
