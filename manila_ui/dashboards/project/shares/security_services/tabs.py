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

from manila_ui.dashboards.project.shares.security_services \
    import tables as security_services_tables


class SecurityServiceTab(tabs.TableTab):
    table_classes = (security_services_tables.SecurityServiceTable,)
    name = _("Security Services")
    slug = "security_services_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_security_services_data(self):
        try:
            security_services = manila.security_service_list(self.request)
        except Exception:
            security_services = []
            exceptions.handle(self.request,
                              _("Unable to retrieve security services"))

        return security_services


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("project/shares/security_services/_detail_overview.html")

    def get_context_data(self, request):
        return {"sec_service": self.tab_group.kwargs['sec_service']}


class SecurityServiceDetailTabs(tabs.TabGroup):
    slug = "security_service_details"
    tabs = (OverviewTab,)
