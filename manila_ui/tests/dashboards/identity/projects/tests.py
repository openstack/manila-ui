# (c) Copyright 2019 SUSE LLC
# All rights reserved.

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


from django.test.utils import override_settings
from django.urls import reverse

from horizon.workflows import views
from openstack_dashboard.api import base
from openstack_dashboard.usage import quotas

from manila_ui.api import manila as manila_api
from manila_ui.tests import helpers as manila_base_test


class UpdateShareQuotaWorkflowTests(manila_base_test.BaseAdminViewTests):

    def setUp(self):
        super(UpdateShareQuotaWorkflowTests, self).setUp()
        self.id = "fake_id"

        # mock functions in manila.py
        self.mock_tenant_quota_get = (
            self.mock_object(manila_api, "tenant_quota_get"))
        self.mock_tenant_quota_get.return_value = (
            self._get_mock_share_quota_data())

        # mock functions in quotas.py
        self.mock_object(quotas, "get_tenant_quota_data")
        self.mock_object(quotas, "get_disabled_quotas").return_value = set()

    def _get_mock_share_quota_data(self):
        quota_data = {
            'shares': 24, 'gigabytes': 333, 'snapshots': 14,
            'snapshot_gigabytes': 444, 'share_networks': 14
        }

        return base.QuotaSet(quota_data)

    @override_settings(EXTRA_STEPS={
        'openstack_dashboard.dashboards.identity.projects.\
         workflows.UpdateQuota': (
            'manila_ui.dashboards.identity.projects.workflows.UpdateShareQuota'
        )}
    )
    def test_tenant_quota_get(self):
        tenant_id = 'fake_tenant_id'
        url = reverse('horizon:identity:projects:update_quotas',
                      args=[tenant_id])
        res = self.client.get(url)

        workflow = res.context['workflow']
        self.assertTemplateUsed(res, views.WorkflowView.template_name)
        step = workflow.get_step("update_share_quotas")

        # Check step UI fields got the fields converted and data correct
        self.assertEqual(step.action.initial['project_id'], tenant_id)
        self.assertEqual(step.action.initial['shares'], 24)
        self.assertEqual(step.action.initial['share_gigabytes'], 333)
        self.assertEqual(step.action.initial['share_snapshot_gigabytes'], 444)
        self.assertEqual(step.action.initial['share_snapshots'], 14)
        self.assertEqual(step.action.initial['share_networks'], 14)
