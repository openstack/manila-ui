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
from django.urls import reverse
from openstack_dashboard.api import neutron
from unittest import mock

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:project:share_snapshots:index')


@ddt.ddt
class SnapshotSnapshotViewTests(test.TestCase):

    def test_create_snapshot_get(self):
        share = test_data.share
        usage_limit = {
            'maxTotalShareGigabytes': 250,
            'totalShareGigabytesUsed': 20,
        }
        url = reverse('horizon:project:share_snapshots:share_snapshot_create',
                      args=[share.id])
        self.mock_object(
            api_manila, "tenant_absolute_limits",
            mock.Mock(return_value=usage_limit))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/share_snapshots/create.html')

    def test_create_snapshot_post(self):
        share = test_data.share
        snapshot = test_data.snapshot
        url = reverse('horizon:project:share_snapshots:share_snapshot_create',
                      args=[share.id])
        formData = {
            'name': 'new_snapshot',
            'description': 'This is test snapshot',
            'method': 'CreateShareSnapshotForm',
            'share_id': share.id,
            'metadata': ''
        }
        self.mock_object(
            api_manila, "share_snapshot_create",
            mock.Mock(return_value=snapshot))
        res = self.client.post(url, formData)
        api_manila.share_snapshot_create.assert_called_once_with(
            mock.ANY,
            share.id,
            name=formData['name'],
            description=formData['description'],
            metadata={})
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_delete_snapshot(self):
        share = test_data.share
        snapshot = test_data.snapshot
        formData = {'action': 'share_snapshots__delete__%s' % snapshot.id}
        self.mock_object(api_manila, "share_snapshot_delete")
        self.mock_object(
            api_manila, "share_snapshot_list",
            mock.Mock(return_value=[snapshot]))
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=[share]))

        res = self.client.post(INDEX_URL, formData)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_snapshot_list.assert_called_once_with(mock.ANY)
        api_manila.share_list.assert_called_once_with(mock.ANY)
        api_manila.share_snapshot_delete.assert_called_once_with(
            mock.ANY, test_data.snapshot.id)

    def test_detail_view(self):
        snapshot = test_data.snapshot
        share = test_data.share
        url = reverse('horizon:project:share_snapshots:share_snapshot_detail',
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
                            "<dd><a href=\"/project/shares/%s/\">%s</a></dd>" %
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
        url = reverse('horizon:project:share_snapshots:share_snapshot_detail',
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
                            "<dd><a href=\"/project/shares/%s/\">%s</a></dd>" %
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
        url = reverse('horizon:project:share_snapshots:share_snapshot_edit',
                      args=[snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(return_value=snapshot))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot.id)
        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/share_snapshots/update.html')

    def test_update_snapshot_post(self):
        snapshot = test_data.snapshot
        url = reverse('horizon:project:share_snapshots:share_snapshot_edit',
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

        self.assertRedirectsNoFollow(res, INDEX_URL)
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
        url = reverse(
            'horizon:project:share_snapshots:share_snapshot_manage_rules',
            args=[snapshot.id])

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(
            res,
            'project/share_snapshots/manage_rules.html')
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
        url = reverse(
            'horizon:project:share_snapshots:share_snapshot_manage_rules',
            args=[snapshot.id])

        res = self.client.get(url)

        self.assertEqual(res.status_code, 302)
        self.assertTemplateNotUsed(
            res, 'project/share_snapshots/manage_rules.html')
        api_manila.share_snapshot_rules_list.assert_called_once_with(
            mock.ANY, snapshot.id)

    def test_create_rule_get(self):
        snapshot = test_data.snapshot
        url = reverse(
            'horizon:project:share_snapshots:share_snapshot_rule_add',
            args=[snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(
                return_value=snapshot))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/share_snapshots/rule_add.html')

    def test_create_rule_get_exception(self):
        snapshot = test_data.snapshot
        url = reverse(
            'horizon:project:share_snapshots:share_snapshot_rule_add',
            args=[snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(
                side_effect=Exception('fake')))

        res = self.client.get(url)

        self.assertEqual(res.status_code, 302)
        self.assertTemplateNotUsed(
            res, 'project/share_snapshots/rule_add.html')

    @ddt.data(None, Exception('fake'))
    def test_create_rule_post(self, exc):
        snapshot = test_data.snapshot
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(return_value=snapshot))
        url = reverse(
            'horizon:project:share_snapshots:share_snapshot_rule_add',
            args=[snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_allow",
            mock.Mock(side_effect=exc))
        formData = {
            'access_type': 'user',
            'method': 'CreateForm',
            'access_to': 'someuser',
        }

        res = self.client.post(url, formData)

        self.assertEqual(res.status_code, 302)
        api_manila.share_snapshot_allow.assert_called_once_with(
            mock.ANY, snapshot.id, access_type=formData['access_type'],
            access_to=formData['access_to'])
        self.assertRedirectsNoFollow(
            res,
            reverse(
                'horizon:project:share_snapshots:share_snapshot_manage_rules',
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
            'horizon:project:share_snapshots:share_snapshot_manage_rules',
            args=[snapshot.id])

        res = self.client.post(url, formData)

        self.assertEqual(res.status_code, 302)
        api_manila.share_snapshot_deny.assert_called_with(
            mock.ANY, snapshot.id, rule.id)
        api_manila.share_snapshot_rules_list.assert_called_with(
            mock.ANY, snapshot.id)

    def test_update_snapshot_metadata_get(self):
        snapshot = self.snapshots.first()
        snapshot_id = str(snapshot.id)
        snapshot.metadata = {'ro': 'se'}
        url = reverse('horizon:project:share_snapshots:update_metadata',
                      args=[snapshot_id])
        self.mock_object(api_manila, "share_snapshot_get",
                         mock.Mock(return_value=snapshot))
        res = self.client.get(url)
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot_id)
        self.assertNoMessages()
        self.assertTemplateUsed(
            res, 'project/share_snapshots/update_metadata.html')
        self.assertEqual(res.context['form'].initial['metadata'], "ro=se\r\n")

    def test_update_snapshot_metadata_post(self):
        snapshot = self.snapshots.first()
        snapshot_id = str(snapshot.id)
        snapshot.metadata = {'ro': 'see'}
        data = {
            'snapshot_id': snapshot_id,
            'metadata': 'ro=se\r\nki=mondo',
        }
        url = reverse('horizon:project:share_snapshots:update_metadata',
                      args=[snapshot_id])
        self.mock_object(api_manila, "share_snapshot_get",
                         mock.Mock(return_value=snapshot))
        self.mock_object(api_manila, "share_snapshot_set_metadata")
        self.mock_object(api_manila, "share_snapshot_delete_metadata")
        res = self.client.post(url, data)
        expected_set_dict = {'ro': 'se', 'ki': 'mondo'}
        api_manila.share_snapshot_set_metadata.assert_called_once_with(
            mock.ANY, snapshot_id, expected_set_dict)
        self.assertRedirectsNoFollow(
            res, reverse('horizon:project:share_snapshots:index'))
        self.assertMessageCount(success=1)

    def test_update_snapshot_metadata_unset_by_key_only_post(self):
        snapshot = self.snapshots.first()
        snapshot_id = str(snapshot.id)
        snapshot.metadata = {'ro': 'se'}
        data = {
            'snapshot_id': snapshot_id,
            'metadata': 'ro',
        }
        url = reverse('horizon:project:share_snapshots:update_metadata',
                      args=[snapshot_id])
        self.mock_object(api_manila, "share_snapshot_get",
                         mock.Mock(return_value=snapshot))
        self.mock_object(api_manila, "share_snapshot_set_metadata")
        self.mock_object(api_manila, "share_snapshot_delete_metadata")
        res = self.client.post(url, data)
        api_manila.share_snapshot_delete_metadata.assert_called_once_with(
            mock.ANY, snapshot_id, ['ro'])
        self.assertFalse(api_manila.share_snapshot_set_metadata.called)
        self.assertMessageCount(success=1)
        self.assertRedirectsNoFollow(
            res, reverse('horizon:project:share_snapshots:index'))

    def test_create_snapshot_post_with_metadata(self):
        share = test_data.share
        snapshot = test_data.snapshot
        url = reverse('horizon:project:share_snapshots:share_snapshot_create',
                      args=[share.id])

        formData = {
            'name': 'metadata_snapshot',
            'description': 'Snapshot with metadata',
            'method': 'CreateShareSnapshotForm',
            'share_id': share.id,
            'metadata': 'project=manila\nenv=testing'
        }
        self.mock_object(
            api_manila, "share_snapshot_create",
            mock.Mock(return_value=snapshot))

        res = self.client.post(url, formData)
        api_manila.share_snapshot_create.assert_called_once_with(
            mock.ANY,
            share.id,
            name=formData['name'],
            description=formData['description'],
            metadata={'project': 'manila', 'env': 'testing'})
        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    def test_update_snapshot_metadata_invalid_formats_post(self):
        snapshot = test_data.snapshot
        snapshot_id = snapshot.id
        mock_snapshot = mock.Mock()
        mock_snapshot.id = snapshot_id
        mock_snapshot.metadata = {}
        self.mock_object(api_manila, "share_snapshot_get",
                         mock.Mock(return_value=mock_snapshot))
        error_404 = Exception("MetadataItemNotFound: Metadata item not found.")
        error_404.code = 404
        mock_delete = self.mock_object(
            api_manila, "share_snapshot_delete_metadata",
            mock.Mock(side_effect=error_404))
        url = reverse('horizon:project:share_snapshots:update_metadata',
                      args=[snapshot_id])
        formData = {
            'method': 'update_metadata_form',
            'snapshot_id': snapshot_id,
            'metadata': '1-b'
        }
        res = self.client.post(url, formData, follow=True)
        mock_delete.assert_called_once()
        msgs = [m.message for m in res.wsgi_request._messages]
        expected = "Each line must contain a 'key=value' pair"
        self.assertTrue(any(expected in m for m in msgs),
                        "Expected message not found in: %s" % msgs)

    def test_share_snapshot_set_metadata(self):
        snapshot = test_data.snapshot
        metadata = {'key1': 'val1', 'key2': 'val2'}
        self.mock_object(api_manila, "share_snapshot_set_metadata")
        api_manila.share_snapshot_set_metadata(
            self.request, snapshot.id, metadata)
        api_manila.share_snapshot_set_metadata.assert_called_once_with(
            self.request, snapshot.id, metadata)

    def test_share_snapshot_delete_metadata(self):
        snapshot = test_data.snapshot
        keys = ['key1', 'key2']
        self.mock_object(api_manila, "share_snapshot_delete_metadata")
        api_manila.share_snapshot_delete_metadata(
            self.request, snapshot.id, keys)
        api_manila.share_snapshot_delete_metadata.assert_called_once_with(
            self.request, snapshot.id, keys)
