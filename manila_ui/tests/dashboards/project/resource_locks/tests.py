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
from unittest import mock

from openstack_auth import policy
from openstack_dashboard import api

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:project:resource_locks:index')


class ResourceLocksViewTests(test.TestCase):

    def test_index_view(self):
        share = test_data.share
        rule = test_data.ip_rule
        locks = test_data.resource_locks_list
        self.mock_object(
            api_manila, "resource_lock_list",
            mock.Mock(return_value=locks))
        self.mock_object(
            api_manila, "share_list",
            mock.Mock(return_value=[share]))
        self.mock_object(
            api_manila, "share_rule_get",
            mock.Mock(return_value=rule))
        self.mock_object(
            api.keystone, "user_list",
            mock.Mock(return_value=[self.user]))
        self.mock_object(
            policy, "check",
            mock.Mock(side_effect=(lambda *args, **kwargs: True)))
        res = self.client.get(INDEX_URL)
        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/resource_locks/index.html')
        shares_table = res.context['shares_locks_table'].data
        rules_table = res.context['rules_locks_table'].data
        self.assertEqual(len(shares_table), 1)
        self.assertEqual(shares_table[0].resource_name, share.name)
        self.assertEqual(len(rules_table), 1)
        self.assertEqual(rules_table[0].access_to, rule.access_to)
        self.assertEqual(api_manila.resource_lock_list.call_count, 1)
        api_manila.resource_lock_list.assert_called_once_with(
            mock.ANY, search_opts={})
        api_manila.share_rule_get.assert_called_once_with(mock.ANY, rule.id)

    def test_update_lock_get(self):
        lock = test_data.lock_1
        self.mock_object(
            api_manila, "resource_lock_get",
            mock.Mock(return_value=lock))
        url = reverse('horizon:project:resource_locks:update', args=[lock.id])
        res = self.client.get(url)
        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/resource_locks/update_lock.html')
        self.assertEqual(
            res.context['form'].initial['lock_reason'], lock.lock_reason)
        api_manila.resource_lock_get.assert_called_once_with(mock.ANY, lock.id)

    def test_update_lock_post(self):
        lock = test_data.lock_1
        new_reason = "Updated reason for lock"
        formData = {
            'method': 'UpdateLockForm',
            'lock_id': lock.id,
            'lock_reason': new_reason,
        }
        self.mock_object(
            api_manila, "resource_lock_get", mock.Mock(return_value=lock))
        self.mock_object(api_manila, "resource_lock_update")
        url = reverse('horizon:project:resource_locks:update', args=[lock.id])
        res = self.client.post(url, formData)
        self.assertNoFormErrors(res)
        expected_url = f"{INDEX_URL}?tab=resource_lock_tabs__shares_tab"
        self.assertRedirectsNoFollow(res, expected_url)
        api_manila.resource_lock_update.assert_called_once_with(
            mock.ANY, lock.id, lock_reason=new_reason)

    def test_delete_lock(self):
        lock = test_data.lock_1
        formData = {'action': 'shares_locks__delete__%s' % lock.id}

        self.mock_object(api_manila, "resource_lock_delete")
        self.mock_object(api_manila, "resource_lock_list",
                         mock.Mock(return_value=test_data.resource_locks_list))
        self.mock_object(api_manila, "share_list",
                         mock.Mock(return_value=test_data.shares_list))
        self.mock_object(api.keystone, "user_list",
                         mock.Mock(return_value=[self.user]))
        self.mock_object(policy, "check",
                         mock.Mock(side_effect=(lambda *args, **kwargs: True)))

        res = self.client.post(INDEX_URL, formData)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.resource_lock_delete.assert_called_once_with(
            mock.ANY, lock.id)

    def test_update_lock_redirect_to_rules_tab(self):
        lock = test_data.lock_2
        formData = {
            'method': 'UpdateLockForm',
            'lock_id': lock.id,
            'lock_reason': 'testing tab redirect',
        }
        self.mock_object(
            api_manila, "resource_lock_get", mock.Mock(return_value=lock))
        self.mock_object(api_manila, "resource_lock_update")
        url = reverse('horizon:project:resource_locks:update', args=[lock.id])
        res = self.client.post(url, formData)
        expected_url = f"{INDEX_URL}?tab=resource_lock_tabs__rules_tab"
        self.assertRedirectsNoFollow(res, expected_url)

    def test_index_view_user_list_failure_shows_id(self):
        lock = test_data.lock_1
        lock.user_id = "non-existent-user-uuid"
        locks = [lock]
        self.mock_object(api_manila, "resource_lock_list",
                         mock.Mock(return_value=locks))
        self.mock_object(api_manila, "share_list",
                         mock.Mock(return_value=[test_data.share]))
        self.mock_object(api.keystone, "user_list",
                         mock.Mock(side_effect=Exception("Keystone down")))
        self.mock_object(policy, "check",
                         mock.Mock(side_effect=(lambda *args, **kwargs: True)))
        res = self.client.get(INDEX_URL)
        self.assertNoMessages()
        shares_table = res.context['shares_locks_table'].data
        self.assertEqual(shares_table[0].user_name, "non-existent-user-uuid")
        api.keystone.user_list.assert_called_once()
