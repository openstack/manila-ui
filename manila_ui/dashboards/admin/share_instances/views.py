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
Admin views for managing share instances.
"""

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.admin.share_instances import tables as si_tables
from manila_ui.dashboards.admin.share_instances import tabs as si_tabs
from manila_ui.dashboards import utils as ui_utils


class ShareInstancesView(tables.MultiTableView):
    table_classes = (
        si_tables.ShareInstancesTable,
    )
    template_name = "admin/share_instances/index.html"
    page_title = _("Share Instances")

    @memoized.memoized_method
    def get_share_instances_data(self):
        try:
            share_instances = manila.share_instance_list(self.request)
        except Exception:
            share_instances = []
            exceptions.handle(
                self.request, _("Unable to retrieve share instances."))
        return share_instances


class ShareInstanceDetailView(tabs.TabView):
    tab_group_class = si_tabs.ShareInstanceDetailTabs
    template_name = 'admin/share_instances/detail.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        share_instance = self.get_data()
        context["share_instance"] = share_instance
        context["page_title"] = (
            _("Share Instance Details: %s") % share_instance.id)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_instance_id = self.kwargs['share_instance_id']
            share_instance = manila.share_instance_get(
                self.request, share_instance_id)
            share_instance.export_locations = (
                manila.share_instance_export_location_list(
                    self.request, share_instance_id))
            export_locations = [
                exp['path'] for exp in share_instance.export_locations
            ]
            share_instance.el_size = ui_utils.calculate_longest_str_size(
                export_locations)
            return share_instance
        except Exception:
            redirect = reverse('horizon:admin:share_instances:index')
            exceptions.handle(
                self.request,
                _('Unable to retrieve share instance details.'),
                redirect=redirect)

    def get_tabs(self, request, *args, **kwargs):
        share_instance = self.get_data()
        return self.tab_group_class(
            request, share_instance=share_instance, **kwargs)
