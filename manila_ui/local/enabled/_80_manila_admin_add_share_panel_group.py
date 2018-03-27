# Copyright 2017 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# The slug of the panel group to be added to HORIZON_CONFIG. Required.
PANEL_GROUP = 'share'
# The display name of the PANEL_GROUP. Required.
PANEL_GROUP_NAME = 'Share'
# The slug of the dashboard the PANEL_GROUP associated with. Required.
PANEL_GROUP_DASHBOARD = 'admin'

EXTRA_TABS = {
    'openstack_dashboard.dashboards.admin.defaults.tabs.DefaultsTabs': (
        'manila_ui.dashboards.admin.defaults.tabs.ShareQuotasTab',
    ),
}
EXTRA_STEPS = {
    'openstack_dashboard.dashboards.identity.projects.workflows.UpdateQuota': (
        'manila_ui.dashboards.identity.projects.workflows.UpdateShareQuota',
    ),
    'openstack_dashboard.dashboards.admin.defaults.workflows.'
    'UpdateDefaultQuotas': (
        'manila_ui.dashboards.admin.defaults.workflows.'
        'UpdateDefaultShareQuotasStep',
    ),
}
