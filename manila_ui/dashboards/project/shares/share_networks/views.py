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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon.utils import memoized
from horizon import workflows

from manila_ui.api import manila
from manila_ui.api import network
from manila_ui.dashboards.project.shares.share_networks import forms \
    as share_net_forms
from manila_ui.dashboards.project.shares.share_networks import tabs \
    as share_net_tabs
from manila_ui.dashboards.project.shares.share_networks \
    import workflows as share_net_workflows
from manila_ui.dashboards import utils

from openstack_dashboard.api import base
from openstack_dashboard.api import neutron


class Update(workflows.WorkflowView):
    workflow_class = share_net_workflows.UpdateShareNetworkWorkflow
    template_name = "project/shares/share_networks/share_network_update.html"
    success_url = 'horizon:project:shares:index'
    page_title = _('Update Share Network')

    def get_initial(self):
        return {'id': self.kwargs["share_network_id"]}

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        context['id'] = self.kwargs['share_network_id']
        return context


class Create(forms.ModalFormView):
    form_class = share_net_forms.Create
    form_id = "create_share_network"
    template_name = 'project/shares/share_networks/create_share_network.html'
    modal_header = _("Create Share Network")
    submit_label = _("Create")
    submit_url = reverse_lazy("horizon:project:shares:create_share_network")
    success_url = 'horizon:project:shares:index'
    page_title = _('Create Share Network')

    def get_success_url(self):
        return reverse(self.success_url)


class Detail(tabs.TabView):
    tab_group_class = share_net_tabs.ShareNetworkDetailTabs
    template_name = 'project/shares/share_networks/detail.html'
    redirect_url = reverse_lazy('horizon:project:shares:index')

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
                try:
                    share_net.neutron_net = neutron.network_get(
                        self.request, share_net.neutron_net_id).name_or_id
                except (
                    neutron.neutron_client.exceptions.NeutronClientException):
                    share_net.neutron_net = _("Unknown")
                try:
                    share_net.neutron_subnet = neutron.subnet_get(
                        self.request, share_net.neutron_subnet_id).name_or_id
                except (
                    neutron.neutron_client.exceptions.NeutronClientException):
                    share_net.neutron_subnet = _("Unknown")
            else:
                try:
                    share_net.nova_net = network.network_get(
                        self.request, share_net.nova_net_id).name_or_id
                except Exception:
                    share_net.nova_net = _("Unknown")

            share_net.sec_services = (
                manila.share_network_security_service_list(
                    self.request, share_net_id))
            for ss in share_net.sec_services:
                ss.type = utils.get_nice_security_service_type(ss)
            server_search_opts = {'share_network_id': share_net_id}
            share_servs = manila.share_server_list(
                self.request,
                search_opts=server_search_opts)
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
