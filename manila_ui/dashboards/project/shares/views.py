# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
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
Views for managing shares.
"""

from django.utils.translation import ugettext_lazy as _
from horizon import tabs

from manila_ui.dashboards.project.shares.security_services \
    import tabs as security_services_tabs
from manila_ui.dashboards.project.shares.share_networks \
    import tabs as share_networks_tabs
from manila_ui.dashboards.project.shares.shares \
    import tabs as shares_tabs
from manila_ui.dashboards.project.shares.snapshots \
    import tabs as snapshots_tabs


class ShareTabs(tabs.TabGroup):
    slug = "share_tabs"
    tabs = (shares_tabs.SharesTab,
            snapshots_tabs.SnapshotsTab,
            share_networks_tabs.ShareNetworkTab,
            security_services_tabs.SecurityServiceTab,)
    sticky = True


class IndexView(tabs.TabbedTableView):
    tab_group_class = ShareTabs
    template_name = "project/shares/index.html"
    page_title = _("Shares")
