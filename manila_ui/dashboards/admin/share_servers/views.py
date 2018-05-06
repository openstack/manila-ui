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
Admin views for managing share servers.
"""

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.admin.share_servers import tables as ss_tables
from manila_ui.dashboards.admin.share_servers import tabs as ss_tabs
from manila_ui.dashboards.admin import utils


class ShareServersView(tables.MultiTableView):
    table_classes = (
        ss_tables.ShareServersTable,
    )
    template_name = "admin/share_servers/index.html"
    page_title = _("Share Servers")

    @memoized.memoized_method
    def get_share_servers_data(self):
        try:
            share_servers = manila.share_server_list(self.request)
        except Exception:
            share_servers = []
            exceptions.handle(
                self.request, _("Unable to retrieve share servers"))
        utils.set_project_name_to_objects(self.request, share_servers)
        return share_servers


class ShareServerDetailView(tabs.TabView):
    tab_group_class = ss_tabs.ShareServerDetailTabs
    template_name = "admin/share_servers/detail.html"
    redirect_url = reverse_lazy('horizon:admin:share_servers:index')

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        share_server = self.get_data()
        share_server_display_name = share_server.id
        context["share_server"] = share_server
        context["share_server_display_name"] = share_server_display_name
        context["page_title"] = _("Share Server Details: %(server_name)s") % {
            'server_name': share_server_display_name}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_serv_id = self.kwargs['share_server_id']
            share_serv = manila.share_server_get(self.request, share_serv_id)
            share_search_opts = {'share_server_id': share_serv.id}
            shares_list = manila.share_list(
                self.request, search_opts=share_search_opts)
            for share in shares_list:
                share.name_or_id = share.name or share.id
            share_serv.shares_list = shares_list
            if not hasattr(share_serv, 'share_network_id'):
                share_serv.share_network_id = None
        except Exception:
            redirect = reverse('horizon:admin:share_servers:index')
            exceptions.handle(
                self.request,
                _('Unable to retrieve share server details.'),
                redirect=redirect)
        return share_serv

    def get_tabs(self, request, *args, **kwargs):
        share_server = self.get_data()
        return self.tab_group_class(
            request, share_server=share_server, **kwargs)
