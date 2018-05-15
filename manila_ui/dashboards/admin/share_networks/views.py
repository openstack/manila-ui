# Copyright 2017 Mirantis, Inc.
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

"""
Admin views for managing share networks.
"""

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon.utils import memoized
from openstack_dashboard.api import base
from openstack_dashboard.api import neutron

from manila_ui.api import manila
from manila_ui.dashboards.admin.share_networks import tables as sn_tables
from manila_ui.dashboards.admin.share_networks import tabs as sn_tabs
from manila_ui.dashboards.admin import utils
from manila_ui.dashboards.project.share_networks import views as p_views


class ShareNetworksView(tables.MultiTableView):
    table_classes = (
        sn_tables.ShareNetworksTable,
    )
    template_name = "admin/share_networks/index.html"
    page_title = _("Share Networks")

    @memoized.memoized_method
    def get_share_networks_data(self):
        try:
            share_networks = manila.share_network_list(
                self.request, detailed=True, search_opts={'all_tenants': True})
            if base.is_service_enabled(self.request, 'network'):
                neutron_net_names = dict(
                    (net.id, net.name)
                    for net in neutron.network_list(self.request))
                neutron_subnet_names = dict(
                    (net.id, net.name)
                    for net in neutron.subnet_list(self.request))
                for sn in share_networks:
                    sn.neutron_net = neutron_net_names.get(
                        sn.neutron_net_id) or sn.neutron_net_id or "-"
                    sn.neutron_subnet = neutron_subnet_names.get(
                        sn.neutron_subnet_id) or sn.neutron_subnet_id or "-"
        except Exception:
            share_networks = []
            exceptions.handle(
                self.request, _("Unable to retrieve share networks"))
        utils.set_project_name_to_objects(self.request, share_networks)
        return share_networks


class ShareNetworkDetailView(p_views.Detail):
    tab_group_class = sn_tabs.ShareNetworkDetailTabs
    template_name = "admin/share_networks/detail.html"
    redirect_url = reverse_lazy("horizon:admin:share_networks:index")
