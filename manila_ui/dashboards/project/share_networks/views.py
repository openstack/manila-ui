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

import re

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon.utils import memoized
from horizon import workflows
from openstack_dashboard.api import base
from openstack_dashboard.api import neutron

from manila_ui.api import manila
from manila_ui.dashboards.project.share_networks import tables as sn_tables
from manila_ui.dashboards.project.share_networks import tabs as sn_tabs
import manila_ui.dashboards.project.share_networks.workflows as sn_workflows
from manila_ui.dashboards import utils


class ShareNetworksView(tables.MultiTableView):
    table_classes = (
        sn_tables.ShareNetworksTable,
    )
    template_name = "admin/share_networks/index.html"
    page_title = _("Share Networks")

    @memoized.memoized_method
    def get_share_networks_data(self):
        try:
            share_networks = manila.share_network_list(
                self.request, detailed=True)
        except Exception:
            share_networks = []
            exceptions.handle(
                self.request, _("Unable to retrieve share networks"))
        share_networks = self.get_filters(share_networks)
        return share_networks

    def get_filters(self, share_networks):
        table = self._tables['share_networks']
        filters = self.get_server_filter_info(table.request, table)
        filter_string = filters['value']
        filter_field = filters['field']
        if filter_string and filter_field:
            filtered_data = []
            for share_network in share_networks:
                if filter_field == 'name':
                    if share_network.name == filter_string:
                        filtered_data.append(share_network)

                if filter_field == 'description':
                    re_string = re.compile(filter_string)
                    if (share_network.description and
                            re.search(re_string,
                                      share_network.description)):
                        filtered_data.append(share_network)
            return filtered_data
        else:
            return share_networks


class Update(workflows.WorkflowView):
    workflow_class = sn_workflows.UpdateShareNetworkWorkflow
    template_name = "project/share_networks/update.html"
    success_url = 'horizon:project:share_networks:index'
    page_title = _('Update Share Network')

    def get_initial(self):
        return {'id': self.kwargs["share_network_id"]}

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        context['id'] = self.kwargs['share_network_id']
        return context


class Create(workflows.WorkflowView):
    workflow_class = sn_workflows.CreateShareNetworkWorkflow
    form_id = "create_share_network"
    submit_url = reverse_lazy(
        "horizon:project:share_networks:share_network_create")
    success_url = reverse_lazy("horizon:project:share_networks:index")
    page_title = _('Create Share Network')


class Detail(tabs.TabView):
    tab_group_class = sn_tabs.ShareNetworkDetailTabs
    template_name = 'project/share_networks/detail.html'
    redirect_url = reverse_lazy('horizon:project:share_networks:index')

    def get_context_data(self, **kwargs):
        context = super(Detail, self).get_context_data(**kwargs)
        share_network = self.get_data()
        share_network_display_name = share_network.name or share_network.id
        context["share_network"] = share_network
        context["share_network_display_name"] = share_network_display_name
        context["page_title"] = _("Share Network Details: "
                                  "%(network_display_name)s") % \
            {'network_display_name': share_network_display_name}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_net_id = self.kwargs['share_network_id']
            share_net = manila.share_network_get(self.request, share_net_id)
            if base.is_service_enabled(self.request, 'network'):
                for subnet in share_net.share_network_subnets:
                    # Neutron Net ID
                    try:
                        subnet["neutron_net"] = neutron.network_get(
                            self.request, subnet["neutron_net_id"]).name_or_id
                    except (
                        neutron.neutron_client.exceptions
                        .NeutronClientException
                        ):
                        subnet["neutron_net"] = _("Unknown")
                    # Neutron Subnet ID
                    try:
                        subnet["neutron_subnet"] = neutron.subnet_get(
                            self.request,
                            subnet["neutron_subnet_id"]).name_or_id
                    except (
                        neutron.neutron_client.exceptions
                        .NeutronClientException
                        ):
                        subnet["neutron_subnet"] = _("Unknown")
            # List all azs if availability_zone is None
            availability_zones = manila.availability_zone_list(self.request)
            az_list = ", ".join([az.name for az in availability_zones])
            for subnet in share_net.share_network_subnets:
                if subnet["availability_zone"] is None:
                    subnet["availability_zone"] = az_list
            share_net.sec_services = (
                manila.share_network_security_service_list(
                    self.request, share_net_id))
            for ss in share_net.sec_services:
                ss.type = utils.get_nice_security_service_type(ss)
            server_search_opts = {'share_network_id': share_net_id}
            try:
                share_servs = manila.share_server_list(
                    self.request,
                    search_opts=server_search_opts)
            #  Non admins won't be able to get share servers
            except Exception:
                share_servs = []
            if share_servs:
                share_net.share_servers = share_servs
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve share network details.'),
                              redirect=self.redirect_url)
        return share_net

    def get_tabs(self, request, *args, **kwargs):
        share_network = self.get_data()
        return self.tab_group_class(request, share_network=share_network,
                                    **kwargs)
