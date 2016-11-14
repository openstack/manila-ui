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

from horizon.test.settings import *  # noqa
from openstack_dashboard.test.settings import *  # noqa

# Load the pluggable dashboard settings
import manila_ui.local.enabled
import openstack_dashboard.enabled
from openstack_dashboard.utils import settings

MANILA_UI_APPS = list(INSTALLED_APPS) + ['manila_ui.dashboards']
settings.update_dashboards(
    [
        manila_ui.local.enabled,
        openstack_dashboard.enabled,
    ],
    HORIZON_CONFIG,
    MANILA_UI_APPS,
)
