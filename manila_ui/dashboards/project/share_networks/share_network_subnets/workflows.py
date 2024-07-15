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
from horizon import messages
from horizon import workflows

from manila_ui.api import manila
from manila_ui.dashboards.project.share_networks \
    import workflows as sn_workflows
from manila_ui.dashboards import utils


class AddShareNetworkSubnetStep(workflows.Step):
    action_class = sn_workflows.AddShareNetworkSubnetAction
    depends_on = ("share_network_id",)
    contributes = ("neutron_net_id", "neutron_subnet_id", "availability_zone")


class CreateShareNetworkSubnetsWorkflow(workflows.Workflow):
    slug = "create_share_network_subnet"
    name = _("Create Share Network Subnet")
    finalize_button_name = _("Create Share Network Subnet")
    success_message = _('')
    failure_message = _('')
    success_url = 'horizon:project:share_networks:index'
    default_steps = (AddShareNetworkSubnetStep,)

    def handle(self, request, context):
        try:
            data = request.POST
            share_network_id = self.context['share_network_id']
            share_network_name = manila.share_network_get(
                request, share_network_id).name
            send_data = {'share_network_id': share_network_id}

            neutron_net_id = context.get('neutron_net_id')
            if neutron_net_id:
                send_data['neutron_net_id'] = utils.transform_dashed_name(
                    neutron_net_id.strip())
                subnet_key = (
                    'subnet-choices-%s' % neutron_net_id.strip()
                )
                if data.get(subnet_key) is not None:
                    send_data['neutron_subnet_id'] = data.get(subnet_key)
            if context['availability_zone']:
                send_data['availability_zone'] = context['availability_zone']
            share_network = manila.share_network_subnet_create(request,
                                                               **send_data)

            messages.success(
                request,
                _('Successfully created share network subnet for: %s') %
                share_network_name)
            return share_network
        except Exception:
            exceptions.handle(request,
                              _('Unable to create share network subnet.'))
            return False
