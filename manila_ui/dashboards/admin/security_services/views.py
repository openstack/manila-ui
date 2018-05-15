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
Admin views for managing security services.
"""

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon.utils import memoized

from manila_ui.api import manila
import manila_ui.dashboards.admin.security_services.tables as ss_tables
import manila_ui.dashboards.admin.security_services.tabs as ss_tabs
from manila_ui.dashboards.admin import utils
import manila_ui.dashboards.project.security_services.views as ss_views


class SecurityServicesView(tables.MultiTableView):
    table_classes = (
        ss_tables.SecurityServicesTable,
    )
    template_name = "admin/security_services/index.html"
    page_title = _("Security Services")

    @memoized.memoized_method
    def get_security_services_data(self):
        try:
            security_services = manila.security_service_list(
                self.request, search_opts={'all_tenants': True})
            utils.set_project_name_to_objects(self.request, security_services)
        except Exception:
            security_services = []
            exceptions.handle(
                self.request, _("Unable to retrieve security services"))
        return security_services


class SecurityServiceDetailView(ss_views.Detail):
    tab_group_class = ss_tabs.SecurityServiceDetailTabs
    template_name = "admin/security_services/detail.html"
    redirect_url = reverse_lazy('horizon:admin:security_services:index')
