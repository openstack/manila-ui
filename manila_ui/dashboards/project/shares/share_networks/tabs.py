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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from manila_ui.api import manila
from manila_ui.api import network
from manila_ui.dashboards.project.shares.share_networks\
    import tables as share_net_tables

from openstack_dashboard.api import base
from openstack_dashboard.api import neutron


class ShareNetworkTab(tabs.TableTab):
    name = _("Share Networks")
    slug = "share_networks_tab"
    template_name = "horizon/common/_detail_table.html"

    def __init__(self, tab_group, request):
        if base.is_service_enabled(request, 'network'):
            self.table_classes = (share_net_tables.NeutronShareNetworkTable,)
        else:
            self.table_classes = (share_net_tables.NovaShareNetworkTable,)
        super(ShareNetworkTab, self).__init__(tab_group, request)

    def get_share_networks_data(self):
        try:
            share_networks = manila.share_network_list(self.request,
                                                       detailed=True)
            if base.is_service_enabled(self.request, 'network'):
                neutron_net_names = dict((net.id, net.name) for net in
                                         neutron.network_list(self.request))
                neutron_subnet_names = dict((net.id, net.name) for net in
                                            neutron.subnet_list(self.request))
                for sn in share_networks:
                    sn.neutron_net = neutron_net_names.get(
                        sn.neutron_net_id) or sn.neutron_net_id or "-"
                    sn.neutron_subnet = neutron_subnet_names.get(
                        sn.neutron_subnet_id) or sn.neutron_subnet_id or "-"
            else:
                nova_net_names = dict(
                    [(net.id, net.label)
                     for net in network.network_list(self.request)])
                for sn in share_networks:
                    sn.nova_net = nova_net_names.get(
                        sn.nova_net_id) or sn.nova_net_id or "-"
        except Exception:
            share_networks = []
            exceptions.handle(self.request,
                              _("Unable to retrieve share networks"))
        return share_networks


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("project/shares/share_networks/_detail_overview.html")

    def get_context_data(self, request):
        return {"share_network": self.tab_group.kwargs['share_network']}


class ShareNetworkDetailTabs(tabs.TabGroup):
    slug = "share_network_details"
    tabs = (OverviewTab,)
