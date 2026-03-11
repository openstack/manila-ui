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
from horizon import exceptions
from horizon import tabs

from manila_ui.dashboards.project.share_networks import tables as sn_tables


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "project/share_networks/_detail.html"

    def get_context_data(self, request):
        return {
            "share_network": self.tab_group.kwargs['share_network'],
        }


class SubnetsTab(tabs.TableTab):
    name = _("Subnets")
    slug = "subnets_tab"
    table_classes = (sn_tables.ShareNetworkSubnetsTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def get_subnets_data(self):
        try:
            share_network = self.tab_group.kwargs['share_network']
            all_subnets = getattr(share_network, 'share_network_subnets', [])
            self._tables[
                self.table_classes[0].Meta.name].kwargs[
                    'share_network_id'] = share_network.id
            filter_string = self.request.GET.get(
                'subnets_tab__filter__q', '').strip().lower()
            if filter_string:
                return [
                    subnet for subnet in all_subnets
                    if filter_string in " ".join(
                        [f"{k}={v}" for k, v in (
                            subnet.get('metadata') or {}).items()]
                    ).lower()
                ]
            return all_subnets
        except Exception:
            exceptions.handle(
                self.request, _("Unable to retrieve share network subnets."))
            return []


class ShareNetworkDetailTabs(tabs.TabGroup):
    slug = "share_network_details"
    tabs = (
        OverviewTab,
        SubnetsTab,
    )
    sticky = False
