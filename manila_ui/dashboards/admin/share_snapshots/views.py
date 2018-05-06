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
Admin views for managing share snapshots.
"""

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.admin.share_snapshots import tables as ss_tables
from manila_ui.dashboards.admin.share_snapshots import tabs as ss_tabs
from manila_ui.dashboards.admin import utils
import manila_ui.dashboards.project.share_snapshots.views as snapshot_views


class ShareSnapshotsView(tables.MultiTableView):
    table_classes = (
        ss_tables.ShareSnapshotsTable,
    )
    template_name = "admin/share_snapshots/index.html"
    page_title = _("Share Snapshots")

    @memoized.memoized_method
    def get_share_snapshots_data(self):
        snapshots = []
        try:
            snapshots = manila.share_snapshot_list(
                self.request, search_opts={'all_tenants': True})
            shares = manila.share_list(self.request)
            share_names = dict([(share.id, share.name or share.id)
                                for share in shares])
            for snapshot in snapshots:
                snapshot.share = share_names.get(snapshot.share_id)
        except Exception:
            msg = _("Unable to retrieve share snapshot list.")
            exceptions.handle(self.request, msg)

        # Gather our projects to correlate against IDs
        utils.set_project_name_to_objects(self.request, snapshots)

        return snapshots


class ShareSnapshotDetailView(snapshot_views.ShareSnapshotDetailView):
    tab_group_class = ss_tabs.SnapshotDetailTabs
    template_name = "admin/share_snapshots/detail.html"
    redirect_url = reverse_lazy("horizon:admin:share_snapshots:index")
