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

from manila_ui.dashboards.project.shares.snapshots \
    import tables as snapshot_tables


class SnapshotsTab(tabs.TableTab):
    table_classes = (snapshot_tables.SnapshotsTable, )
    name = _("Snapshots")
    slug = "snapshots_tab"
    template_name = "horizon/common/_detail_table.html"

    def _set_id_if_nameless(self, snapshots):
        for snap in snapshots:
            if not snap.name:
                snap.name = snap.id

    def get_snapshots_data(self):
        try:
            snapshots = manila.share_snapshot_list(self.request)
            shares = manila.share_list(self.request)
            share_names = dict([(share.id, share.name or share.id)
                                for share in shares])
            for snapshot in snapshots:
                snapshot.share = share_names.get(snapshot.share_id)
        except Exception:
            msg = _("Unable to retrieve share snapshots list.")
            exceptions.handle(self.request, msg)
            return []
        # Gather our tenants to correlate against IDs
        return snapshots


class SnapshotOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("project/shares/snapshots/"
                     "_snapshot_detail_overview.html")

    def get_context_data(self, request):
        return {"snapshot": self.tab_group.kwargs['snapshot']}


class SnapshotDetailTabs(tabs.TabGroup):
    slug = "snapshot_details"
    tabs = (SnapshotOverviewTab,)
