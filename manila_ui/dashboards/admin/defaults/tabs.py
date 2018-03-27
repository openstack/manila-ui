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

from openstack_dashboard import api

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.admin.defaults import tables


class ShareQuotasTab(tabs.TableTab):
    table_classes = (tables.ShareQuotasTable,)
    name = _("Share Quotas")
    slug = "shared_quotas"
    template_name = ("horizon/common/_detail_table.html")

    def get_share_quotas_data(self):
        request = self.tab_group.request
        tenant_id = request.user.tenant_id
        try:
            data = api_manila.default_quota_get(request, tenant_id)
        except Exception:
            data = []
            exceptions.handle(self.request,
                              _('Unable to get manila default quota.'))
        return data

    def allowed(self, request):
        return api.base.is_service_enabled(request, 'share')
