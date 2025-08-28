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

from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from django.utils.translation import pgettext_lazy
from horizon import tables
from openstack_dashboard.api import base
from openstack_dashboard.api import neutron

from manila_ui.api import manila
from manila_ui.dashboards.project.share_networks.share_network_subnets \
    import tables as subnet_tables

DELETABLE_STATES = ("INACTIVE", "ERROR")
EDITABLE_STATES = ("INACTIVE", )


class Create(tables.LinkAction):
    name = "create_share_network"
    verbose_name = _("Create Share Network")
    url = "horizon:project:share_networks:share_network_create"
    classes = ("ajax-modal", "btn-create")
    icon = "plus"
    policy_rules = (("share", "share_network:create"),)


class Delete(tables.DeleteAction):
    policy_rules = (("share", "share_network:delete"),)

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            "Delete Share Network",
            "Delete Share Networks",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            "Deleted Share Network",
            "Deleted Share Networks",
            count
        )

    def delete(self, request, obj_id):
        manila.share_network_delete(request, obj_id)

    def allowed(self, request, obj=None):
        if obj:
            # NOTE: leave it True until statuses become used
            # return obj.status in DELETABLE_STATES
            return True
        return True


class EditShareNetwork(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Share Network")
    url = "horizon:project:share_networks:share_network_update"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share_network:update"),)

    def allowed(self, request, obj_id):
        # sn = manila.share_network_get(request, obj_id)
        # return sn.status in EDITABLE_STATES
        # NOTE: leave it always True, until statuses become used
        return True


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, share_net_id):
        share_net = manila.share_network_get(request, share_net_id)
        neutron_enabled = base.is_service_enabled(request, 'network')
        if neutron_enabled:
            share_net.neutron_net = neutron.network_get(
                request, share_net.neutron_net_id).name_or_id
            share_net.neutron_subnet = neutron.subnet_get(
                request, share_net.neutron_subnet_id).name_or_id
        return share_net


class ShareNetworksFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = (
        ('name', _("Name") + " ", True),
        ('description', _("Description") + " ", True),
    )


class ShareNetworksTable(tables.DataTable):
    STATUS_CHOICES = (
        ("ACTIVE", True),
        ("INACTIVE", True),
        ("ERROR", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("ACTIVE", pgettext_lazy("Current status of share network",
                                 "Active")),
        ("INACTIVE", pgettext_lazy("Current status of share network",
                                   "Inactive")),
        ("ERROR", pgettext_lazy("Current status of share network", "Error")),
    )
    name = tables.WrappingColumn(
        "name", verbose_name=_("Name"),
        link="horizon:project:share_networks:share_network_detail")
    description = tables.WrappingColumn(
        "description", verbose_name=_("Description"))

    def get_object_display(self, share_network):
        return share_network.name or str(share_network.id)

    def get_object_id(self, share_network):
        return str(share_network.id)

    class Meta(object):
        name = "share_networks"
        verbose_name = _("Share Networks")
        table_actions = (
            ShareNetworksFilterAction,
            Create,
            Delete,
        )
        row_class = UpdateRow
        row_actions = (
            EditShareNetwork,
            Delete,
            subnet_tables.CreateShareNetworkSubnet,
        )
