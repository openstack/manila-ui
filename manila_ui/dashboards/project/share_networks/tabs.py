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
from horizon import tabs


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "project/share_networks/_detail.html"

    def get_context_data(self, request):
        return {"share_network": self.tab_group.kwargs['share_network']}


class ShareNetworkDetailTabs(tabs.TabGroup):
    slug = "share_network_details"
    tabs = (
        OverviewTab,
    )
