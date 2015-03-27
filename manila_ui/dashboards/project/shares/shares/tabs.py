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

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from manila_ui.api import manila

from manila_ui.dashboards.project.shares.shares \
    import tables as share_tables
from manila_ui.dashboards import utils


class SharesTab(tabs.TableTab):
    table_classes = (share_tables.SharesTable, )
    name = _("Shares")
    slug = "shares_tab"
    template_name = "horizon/common/_detail_table.html"

    def _set_id_if_nameless(self, shares):
        for share in shares:
            if not share.name:
                share.name = share.id

    def get_shares_data(self):
        share_nets_names = {}
        share_nets = manila.share_network_list(self.request)
        for share_net in share_nets:
            share_nets_names[share_net.id] = share_net.name
        try:
            shares = manila.share_list(self.request)
            for share in shares:
                share.share_network = \
                    share_nets_names.get(share.share_network_id) or \
                    share.share_network_id
                meta_str = utils.metadata_to_str(share.metadata)
                share.metadata = mark_safe(meta_str)

            snapshots = manila.share_snapshot_list(self.request, detailed=True)
            share_ids_with_snapshots = []
            for snapshot in snapshots:
                share_ids_with_snapshots.append(snapshot.to_dict()['share_id'])
            for share in shares:
                if share.to_dict()['id'] in share_ids_with_snapshots:
                    setattr(share, 'has_snapshot', True)
                else:
                    setattr(share, 'has_snapshot', False)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve share list.'))
            return []
        # Gather our tenants to correlate against IDs
        return shares


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "project/shares/shares/_detail_overview.html"

    def get_context_data(self, request):
        return {"share": self.tab_group.kwargs['share']}


class ShareDetailTabs(tabs.TabGroup):
    slug = "share_details"
    tabs = (OverviewTab,)
