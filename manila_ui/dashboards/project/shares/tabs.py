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

from manila_ui.api import manila
from manila_ui.dashboards.project.shares import tables as shares_tables


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "project/shares/_detail.html"

    def get_context_data(self, request):
        share = self.tab_group.kwargs['share']
        return {"share": share}


class ExportLocationsTab(tabs.TableTab):
    name = _("Export Locations")
    slug = "export_locations_tab"
    table_classes = (shares_tables.ExportLocationsTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def get_export_locations_data(self):
        try:
            share = self.tab_group.kwargs['share']
            self._tables[
                self.table_classes[0].Meta.name].kwargs['share_id'] = share.id
            if not hasattr(share, 'export_locations'):
                try:
                    share.export_locations = manila.share_export_location_list(
                        self.request, share.id)
                except Exception:
                    share.export_locations = []
            all_locations = getattr(share, 'export_locations', [])
            filter_string = self.request.GET.get(
                'export_locations__filter__q', '').strip().lower()
            if filter_string:
                return [
                    el for el in all_locations
                    if filter_string in " ".join(
                        [f"{k}={v}" for k, v in el.metadata.items()]).lower()
                ]
            return all_locations
        except Exception:
            exceptions.handle(
                self.request, _("Unable to retrieve export locations."))
            return []


class ShareDetailTabs(tabs.TabGroup):
    slug = "share_details"
    tabs = (
        OverviewTab,
        ExportLocationsTab,
    )
    sticky = False
