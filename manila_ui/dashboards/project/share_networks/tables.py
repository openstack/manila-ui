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

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from django.utils.translation import pgettext_lazy
from horizon import tables
from openstack_dashboard.api import base
from openstack_dashboard.api import neutron

from manila_ui.api import manila
from manila_ui.dashboards.project.share_networks.share_network_subnets \
    import tables as subnet_tables
from manila_ui.dashboards import utils

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


class UpdateShareNetworkSubnetMetadata(tables.LinkAction):
    name = "update_metadata"
    verbose_name = _("Edit Metadata")
    url = "horizon:project:share_networks:update_subnet_metadata"
    classes = ("ajax-modal",)
    icon = "pencil"
    policy_rules = (("share", "share_network_subnet:update_metadata"),)

    def get_link_url(self, datum):
        share_network_id = self.table.kwargs['share_network_id']
        return reverse(self.url, args=(share_network_id, datum['id']))


def get_metadata(subnet):
    metadata = getattr(subnet, 'metadata', subnet.get('metadata', {}))
    if not metadata:
        return _("-")
    return utils.metadata_to_str(metadata)


def get_network_link(datum):
    net_id = datum.get('neutron_net_id')
    if net_id and datum.get('neutron_net') != _("Unknown"):
        try:
            return reverse("horizon:project:networks:detail", args=(net_id,))
        except Exception:
            return None
    return None


def get_subnet_link(datum):
    sub_id = datum.get('neutron_subnet_id')
    sub_name = datum.get('neutron_subnet')
    if sub_id and sub_name != _("Unknown"):
        try:
            return reverse("horizon:project:networks:subnets:detail",
                           args=(sub_id,))
        except Exception:
            try:
                return reverse("horizon:project:networks:subnets:details",
                               args=(sub_id,))
            except Exception:
                return None
    return None


class ShareNetworkSubnetsTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"))
    neutron_net = tables.Column(
        "neutron_net",
        verbose_name=_("Neutron Network"),
        link=get_network_link
    )
    neutron_subnet = tables.Column(
        "neutron_subnet",
        verbose_name=_("Neutron Subnet"),
        link=get_subnet_link
    )
    availability_zone = tables.Column(
        "availability_zone",
        verbose_name=_("Availability Zone")
    )
    metadata = tables.Column(get_metadata, verbose_name=_("Metadata"))

    class Meta(object):
        name = "subnets"
        verbose_name = _("Subnets")
        table_actions = (tables.FilterAction,)
        row_actions = (UpdateShareNetworkSubnetMetadata,)

    def get_object_id(self, datum):
        return datum.get('id')
