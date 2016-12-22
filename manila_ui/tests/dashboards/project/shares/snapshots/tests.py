# Copyright 2014 NetApp, Inc.
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

import ddt
from django.core.urlresolvers import reverse
import mock

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project.shares import test_data
from manila_ui.tests import helpers as test

from openstack_dashboard.api import neutron
from openstack_dashboard.usage import quotas

SHARE_INDEX_URL = reverse('horizon:project:shares:index')
SHARE_SNAPSHOTS_TAB_URL = reverse('horizon:project:shares:snapshots_tab')


@ddt.ddt
class SnapshotSnapshotViewTests(test.TestCase):

    def test_create_snapshot_get(self):
        share = test_data.share
        usage_limit = {
            'maxTotalShareGigabytes': 250,
            'totalShareGigabytesUsed': 20,
        }
        url = reverse('horizon:project:shares:create_snapshot',
                      args=[share.id])
        self.mock_object(
            quotas, "tenant_limit_usages", mock.Mock(return_value=usage_limit))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertNoMessages()
        self.assertTemplateUsed(
            res, 'project/shares/snapshots/create_snapshot.html')

    def test_create_snapshot_post(self):
        share = test_data.share
        snapshot = test_data.snapshot
        url = reverse('horizon:project:shares:create_snapshot',
                      args=[share.id])
        formData = {
            'name': 'new_snapshot',
            'description': 'This is test snapshot',
            'method': 'CreateForm',
            'size': 1,
            'type': 'NFS',
            'share_id': share.id,
        }
        self.mock_object(
            api_manila, "share_snapshot_create",
            mock.Mock(return_value=snapshot))

        res = self.client.post(url, formData)

        api_manila.share_snapshot_create.assert_called_once_with(
            mock.ANY, share.id, formData['name'], formData['description'])
        self.assertRedirectsNoFollow(res, SHARE_SNAPSHOTS_TAB_URL)

    def test_delete_snapshot(self):
        share = test_data.share
        snapshot = test_data.snapshot
        formData = {'action': 'snapshots__delete__%s' % snapshot.id}
        self.mock_object(api_manila, "share_snapshot_delete")
        self.mock_object(
            api_manila, "share_snapshot_list",
            mock.Mock(return_value=[snapshot]))
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=[share]))
        url = reverse('horizon:project:shares:index')

        res = self.client.post(url, formData)

        api_manila.share_snapshot_delete.assert_called_once_with(
            mock.ANY, test_data.snapshot.id)
        api_manila.share_snapshot_list.assert_called_once_with(mock.ANY)
        api_manila.share_list.assert_called_once_with(mock.ANY)
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)

    def test_detail_view(self):
        snapshot = test_data.snapshot
        share = test_data.share
        url = reverse('horizon:project:shares:snapshot-detail',
                      args=[snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(return_value=snapshot))
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))

        res = self.client.get(url)

        self.assertContains(res, "<h1>Snapshot Details: %s</h1>"
                                 % snapshot.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.id, 1, 200)
        self.assertContains(res,
                            "<dd><a href=\"/admin/shares/%s/\">%s</a></dd>" %
                            (snapshot.share_id, share.name), 1, 200)
        self.assertContains(res, "<dd>%s GiB</dd>" % snapshot.size, 1, 200)
        self.assertNoMessages()
        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot.id)

    def test_detail_view_with_mount_support(self):
        snapshot = test_data.snapshot_mount_support
        share = test_data.share_mount_snapshot
        rules = [test_data.ip_rule, test_data.user_rule, test_data.cephx_rule]
        export_locations = test_data.user_snapshot_export_locations
        url = reverse('horizon:project:shares:snapshot-detail',
                      args=[snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(return_value=snapshot))
        self.mock_object(
            api_manila, "share_snapshot_rules_list", mock.Mock(
                return_value=rules))
        self.mock_object(
            api_manila, "share_snap_export_location_list", mock.Mock(
                return_value=export_locations))
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))

        res = self.client.get(url)

        self.assertContains(res, "<h1>Snapshot Details: %s</h1>"
                                 % snapshot.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.id, 1, 200)
        self.assertContains(res,
                            "<dd><a href=\"/admin/shares/%s/\">%s</a></dd>" %
                            (snapshot.share_id, share.name), 1, 200)
        self.assertContains(res, "<dd>%s GiB</dd>" % snapshot.size, 1, 200)
        for el in export_locations:
            self.assertContains(res, "value=\"%s\"" % el.path, 1, 200)
        for rule in rules:
            self.assertContains(res, "<dt>%s</dt>" % rule.access_type, 1, 200)
            self.assertContains(
                res, "<div><b>Access to: </b>%s</div>" % rule.access_to,
                1, 200)
        self.assertContains(
            res, "<div><b>Status: </b>active</div>", len(rules), 200)
        self.assertNoMessages()
        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot.id)
        api_manila.share_snapshot_rules_list.assert_called_once_with(
            mock.ANY, snapshot.id)
        api_manila.share_snap_export_location_list.assert_called_once_with(
            mock.ANY, snapshot)

    def test_update_snapshot_get(self):
        snapshot = test_data.snapshot
        url = reverse('horizon:project:shares:edit_snapshot',
                      args=[snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(return_value=snapshot))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot.id)
        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/shares/snapshots/update.html')

    def test_update_snapshot_post(self):
        snapshot = test_data.snapshot
        url = reverse('horizon:project:shares:edit_snapshot',
                      args=[snapshot.id])
        formData = {
            'method': 'UpdateForm',
            'name': snapshot.name,
            'description': snapshot.description,
        }
        self.mock_object(api_manila, "share_snapshot_update")
        self.mock_object(api_manila, "share_snapshot_get",
                         mock.Mock(return_value=snapshot))

        res = self.client.post(url, formData)

        self.assertRedirectsNoFollow(res, SHARE_SNAPSHOTS_TAB_URL)
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot.id)
        api_manila.share_snapshot_update.assert_called_once_with(
            mock.ANY, snapshot.id, formData['name'], formData['description'])

    def test_list_rules(self):
        snapshot = test_data.snapshot
        rules = [test_data.ip_rule, test_data.user_rule, test_data.cephx_rule]

        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(
                return_value=snapshot))
        self.mock_object(
            api_manila, "share_snapshot_rules_list", mock.Mock(
                return_value=rules))
        url = reverse('horizon:project:shares:snapshot_manage_rules',
                      args=[snapshot.id])

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'project/shares/snapshots/manage_rules.html')
        api_manila.share_snapshot_rules_list.assert_called_once_with(
            mock.ANY, snapshot.id)

    def test_list_rules_exception(self):
        snapshot = test_data.snapshot

        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(
                return_value=snapshot))
        self.mock_object(
            api_manila, "share_snapshot_rules_list",
            mock.Mock(side_effect=Exception('fake')))
        url = reverse('horizon:project:shares:snapshot_manage_rules',
                      args=[snapshot.id])

        res = self.client.get(url)

        self.assertEqual(res.status_code, 302)
        self.assertTemplateNotUsed(
            res, 'project/shares/snapshots/manage_rules.html')
        api_manila.share_snapshot_rules_list.assert_called_once_with(
            mock.ANY, snapshot.id)

    def test_create_rule_get(self):
        snapshot = test_data.snapshot
        url = reverse('horizon:project:shares:snapshot_rule_add',
                      args=[snapshot.id])

        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(
                return_value=snapshot))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/shares/snapshots/rule_add.html')

    def test_create_rule_get_exception(self):
        snapshot = test_data.snapshot
        url = reverse('horizon:project:shares:snapshot_rule_add',
                      args=[snapshot.id])

        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(
                side_effect=Exception('fake')))

        res = self.client.get(url)

        self.assertEqual(res.status_code, 302)
        self.assertTemplateNotUsed(
            res, 'project/shares/snapshots/rule_add.html')

    @ddt.data(None, Exception('fake'))
    def test_create_rule_post(self, exc):
        snapshot = test_data.snapshot

        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(
                return_value=snapshot))
        url = reverse('horizon:project:shares:snapshot_rule_add',
                      args=[snapshot.id])
        self.mock_object(api_manila, "share_snapshot_allow",
                         mock.Mock(side_effect=exc))

        formData = {
            'access_type': 'user',
            'method': u'CreateForm',
            'access_to': 'someuser',
        }

        res = self.client.post(url, formData)

        self.assertEqual(res.status_code, 302)
        api_manila.share_snapshot_allow.assert_called_once_with(
            mock.ANY, snapshot.id, access_type=formData['access_type'],
            access_to=formData['access_to'])
        self.assertRedirectsNoFollow(
            res,
            reverse('horizon:project:shares:snapshot_manage_rules',
                    args=[snapshot.id])
        )

    @ddt.data(None, Exception('fake'))
    def test_delete_rule(self, exc):
        snapshot = test_data.snapshot
        rule = test_data.ip_rule
        formData = {'action': 'rules__delete__%s' % rule.id}

        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(
                return_value=snapshot))
        self.mock_object(api_manila, "share_snapshot_deny",
                         mock.Mock(side_effect=exc))
        self.mock_object(
            api_manila, "share_snapshot_rules_list", mock.Mock(
                return_value=[rule]))
        url = reverse(
            'horizon:project:shares:snapshot_manage_rules',
            args=[snapshot.id])

        res = self.client.post(url, formData)

        self.assertEqual(res.status_code, 302)
        api_manila.share_snapshot_deny.assert_called_with(
            mock.ANY, snapshot.id, rule.id)
        api_manila.share_snapshot_rules_list.assert_called_with(
            mock.ANY, snapshot.id)
