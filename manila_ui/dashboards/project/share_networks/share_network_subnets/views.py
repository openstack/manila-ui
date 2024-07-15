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
from horizon import workflows

from manila_ui.dashboards.project.share_networks.share_network_subnets \
    import workflows as subnet_workflows


class CreateSubnet(workflows.WorkflowView):
    workflow_class = subnet_workflows.CreateShareNetworkSubnetsWorkflow
    success_url = 'horizon:project:share_networks:index'
    page_title = _('Create Share Network Subnet')

    def get_initial(self):
        return {'share_network_id': self.kwargs["share_network_id"]}
