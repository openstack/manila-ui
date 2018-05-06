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

from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables
from openstack_dashboard.api import base
from openstack_dashboard.api import neutron

from manila_ui.api import manila
from manila_ui.api import network


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
        return ungettext_lazy(
            u"Delete Share Network",
            u"Delete Share Networks",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Share Network",
            u"Deleted Share Networks",
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
        else:
            share_net.nova_net = network.network_get(
                request, share_net.nova_net_id).name_or_id
        return share_net


class ShareNetworksTable(tables.DataTable):
    STATUS_CHOICES = (
        ("ACTIVE", True),
        ("INACTIVE", True),
        ("ERROR", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("ACTIVE", pgettext_lazy("Current status of share network",
                                 u"Active")),
        ("INACTIVE", pgettext_lazy("Current status of share network",
                                   u"Inactive")),
        ("ERROR", pgettext_lazy("Current status of share network", u"Error")),
    )
    name = tables.WrappingColumn(
        "name", verbose_name=_("Name"),
        link="horizon:project:share_networks:share_network_detail")
    neutron_net = tables.Column("neutron_net", verbose_name=_("Neutron Net"))
    neutron_subnet = tables.Column(
        "neutron_subnet", verbose_name=_("Neutron Subnet"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    network_type = tables.Column(
        "network_type", verbose_name=_("Network Type"))
    segmentation_id = tables.Column(
        "segmentation_id", verbose_name=_("Segmentation Id"))

    def get_object_display(self, share_network):
        return share_network.name or str(share_network.id)

    def get_object_id(self, share_network):
        return str(share_network.id)

    class Meta(object):
        name = "share_networks"
        verbose_name = _("Share Networks")
        table_actions = (
            tables.NameFilterAction,
            Create,
            Delete,
        )
        row_class = UpdateRow
        row_actions = (
            EditShareNetwork,
            Delete,
        )
