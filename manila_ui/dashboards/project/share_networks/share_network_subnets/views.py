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

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import workflows

from manila_ui.api import manila
from manila_ui.dashboards.project.share_networks.share_network_subnets \
    import forms as sn_forms
from manila_ui.dashboards.project.share_networks.share_network_subnets \
    import workflows as subnet_workflows


class CreateSubnet(workflows.WorkflowView):
    workflow_class = subnet_workflows.CreateShareNetworkSubnetsWorkflow
    success_url = 'horizon:project:share_networks:index'
    page_title = _('Create Share Network Subnet')

    def get_initial(self):
        return {'share_network_id': self.kwargs["share_network_id"]}


class UpdateShareNetworkSubnetMetadataView(forms.ModalFormView):
    form_class = sn_forms.UpdateShareNetworkSubnetMetadataForm
    form_id = "update_subnet_metadata_form"
    template_name = 'project/share_networks/update_subnet_metadata.html'
    modal_header = _("Edit Share Network Subnet Metadata")
    modal_id = "update_subnet_metadata_modal"
    submit_label = _("Save Changes")
    submit_url = "horizon:project:share_networks:update_subnet_metadata"
    page_title = _("Edit Share Network Subnet Metadata")

    def get_object(self):
        """Fetch the subnet for initial form data."""
        if not hasattr(self, "_object"):
            share_network_id = self.kwargs['share_network_id']
            subnet_id = self.kwargs['subnet_id']
            try:
                self._object = manila.share_network_subnet_get(
                    self.request, share_network_id, subnet_id)
            except Exception:
                msg = _('Unable to retrieve the share network subnet.')
                url = reverse(
                    'horizon:project:share_networks:share_network_detail',
                    args=[share_network_id])
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_cancel_url(self):
        return reverse("horizon:project:share_networks:share_network_detail",
                       args=[self.kwargs['share_network_id']])

    def get_context_data(self, **kwargs):
        """Ensure the 'Save' button posts to the right URL."""
        context = super(UpdateShareNetworkSubnetMetadataView,
                        self).get_context_data(**kwargs)
        context['share_network_id'] = self.kwargs['share_network_id']
        args = (self.kwargs['share_network_id'], self.kwargs['subnet_id'])
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        """Pass the current metadata to the form."""
        subnet = self.get_object()
        return {
            'share_network_id': self.kwargs['share_network_id'],
            'subnet_id': self.kwargs['subnet_id'],
            'metadata': getattr(subnet, 'metadata', {})
        }

    def get_success_url(self):
        base_url = reverse(
            "horizon:project:share_networks:share_network_detail",
            args=[self.kwargs['share_network_id']])
        return f"{base_url}?tab=share_network_details__subnets_tab"
