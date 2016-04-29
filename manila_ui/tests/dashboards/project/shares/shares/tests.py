# Copyright (c) 2014 NetApp, Inc.
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
import mock
import six

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project.shares import test_data
from manila_ui.tests import helpers as test

from openstack_dashboard.api import neutron
from openstack_dashboard.api import nova
from openstack_dashboard.usage import quotas

SHARE_INDEX_URL = reverse('horizon:project:shares:index')


class ShareViewTests(test.TestCase):

    class FakeAZ(object):
        def __init__(self, name):
            self.zoneName = name

    def setUp(self):
        super(ShareViewTests, self).setUp()
        self.fake_share_type = mock.Mock()
        self.fake_share_type.name = 'fake'
        self.fake_share_type.id = 'fake_id'
        self.fake_share_type.get_keys = mock.Mock(
            return_value={'driver_handles_share_servers': 'True'})
        self.share = test_data.share
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=self.share))

    @mock.patch.object(nova, 'availability_zone_list')
    def test_create_share(self, az_list):
        url = reverse('horizon:project:shares:create')
        share_net = test_data.active_share_network
        share_nets = [share_net]
        formData = {
            'name': u'new_share',
            'description': u'This is test share',
            'method': u'CreateForm',
            'share_network': share_net.id,
            'size': 1,
            'share_proto': u'NFS',
            'share_type': 'fake',
            'share-network-choices-fake': share_net.id,
            'availability_zone': 'fake_az',
        }

        az_list.return_value = [self.FakeAZ('fake_az'), ]
        self.mock_object(api_manila, "share_create")
        self.mock_object(
            api_manila, "share_snapshot_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_manila, "share_network_list",
            mock.Mock(return_value=share_nets))
        self.mock_object(
            api_manila, "share_type_list",
            mock.Mock(return_value=[self.fake_share_type, ]))

        self.client.post(url, formData)

        api_manila.share_create.assert_called_once_with(
            mock.ANY, size=formData['size'], name=formData['name'],
            description=formData['description'], proto=formData['share_proto'],
            snapshot_id=None, is_public=False, share_network=share_net.id,
            metadata={}, share_type=formData['share_type'],
            availability_zone=formData['availability_zone'])
        api_manila.share_snapshot_list.assert_called_once_with(mock.ANY)
        api_manila.share_network_list.assert_called_once_with(mock.ANY)
        api_manila.share_type_list.assert_called_once_with(mock.ANY)

    @mock.patch.object(nova, 'availability_zone_list')
    def test_create_share_from_snapshot(self, mock_az_list):
        share_net = test_data.active_share_network
        share_nets = [share_net]
        snapshot = test_data.snapshot
        url = reverse('horizon:project:shares:create')
        formData = {
            'name': u'new_share',
            'description': u'This is test share from snapshot',
            'method': u'CreateForm',
            'share_network': share_net.id,
            'size': snapshot.size,
            'share_proto': 'NFS',
            'share_type': 'fake',
            'share_source_type': 'snapshot',
            'snapshot': snapshot.id,
            'share-network-choices-fake': share_net.id,
            'availability_zone': 'fake_az',
        }
        mock_az_list.return_value = [self.FakeAZ('fake_az'), ]
        self.mock_object(api_manila, "share_create")
        self.mock_object(
            api_manila, "share_snapshot_list",
            mock.Mock(return_value=[snapshot]))
        self.mock_object(
            api_manila, "share_snapshot_get", mock.Mock(return_value=snapshot))
        self.mock_object(
            api_manila, "share_network_list",
            mock.Mock(return_value=share_nets))
        self.mock_object(
            api_manila, "share_type_list",
            mock.Mock(return_value=[self.fake_share_type, ]))

        res = self.client.post(url, formData)

        mock_az_list.assert_called_once_with(mock.ANY)
        api_manila.share_snapshot_list.assert_called_once_with(mock.ANY)
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, snapshot.id)
        api_manila.share_network_list.assert_called_once_with(mock.ANY)
        api_manila.share_type_list.assert_called_once_with(mock.ANY)
        api_manila.share_create.assert_called_with(
            mock.ANY, size=formData['size'], name=formData['name'],
            description=formData['description'], proto=formData['share_proto'],
            snapshot_id=snapshot.id, is_public=False,
            share_network=share_net.id, metadata={},
            share_type=formData['share_type'],
            availability_zone=formData['availability_zone'])
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)

    def test_delete_share(self):
        formData = {'action': 'shares__delete__%s' % self.share.id}
        self.mock_object(
            api_manila, "share_snapshot_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_manila, "share_network_list", mock.Mock(return_value=[]))
        self.mock_object(api_manila, "share_delete")
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=[self.share]))
        url = reverse('horizon:project:shares:index')

        res = self.client.post(url, formData)

        api_manila.share_network_list.assert_called_once_with(mock.ANY)
        api_manila.share_snapshot_list.assert_called_once_with(
            mock.ANY, detailed=True)
        api_manila.share_list.assert_called_with(mock.ANY)
        api_manila.share_delete.assert_called_with(
            mock.ANY, self.share.id)
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)

    def test_detail_view(self):
        share_net = test_data.active_share_network
        rules = [test_data.ip_rule, test_data.user_rule, test_data.cephx_rule]
        export_locations = test_data.export_locations
        url = reverse('horizon:project:shares:detail', args=[self.share.id])
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))
        self.mock_object(
            api_manila, "share_network_get", mock.Mock(return_value=share_net))
        self.mock_object(
            api_manila, "share_rules_list", mock.Mock(return_value=rules))
        self.mock_object(
            api_manila, "share_export_location_list",
            mock.Mock(return_value=export_locations))

        res = self.client.get(url)

        self.assertContains(
            res, "<h1>Share Details: %s</h1>" % self.share.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % self.share.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % self.share.id, 1, 200)
        self.assertContains(res, "<dd>%s GiB</dd>" % self.share.size, 1, 200)
        self.assertContains(
            res, "<dd>%s</dd>" % self.share.share_proto, 1, 200)
        self.assertContains(
            res, "<dd>%s</dd>" % self.share.availability_zone, 1, 200)
        for el in export_locations:
            self.assertContains(res, "value=\"%s\"" % el.path, 1, 200)
            self.assertContains(
                res, "<div><b>Preferred:</b> %s</div>" % el.preferred, 1, 200)
            self.assertContains(
                res, "<div><b>Is admin only:</b> %s</div>" % el.is_admin_only,
                1, 200)
        self.assertContains(
            res, ("<div><b>Share Instance ID:</b> %s</div>" %
                  export_locations[0].share_instance_id),
            2, 200)
        for rule in rules:
            self.assertContains(res, "<dt>%s</dt>" % rule.access_type, 1, 200)
            self.assertContains(res, "<dd>%s</dd>" % rule.access_to, 1, 200)
        self.assertNoMessages()
        api_manila.share_rules_list.assert_called_once_with(
            mock.ANY, self.share.id)
        api_manila.share_export_location_list.assert_called_once_with(
            mock.ANY, self.share.id)
        self.assertEqual(3, neutron.is_service_enabled.call_count)

    def test_update_share(self):
        self.mock_object(api_manila, "share_update")
        formData = {
            'method': 'UpdateForm',
            'name': self.share.name,
            'description': self.share.description,
            'is_public': False,
        }
        url = reverse('horizon:project:shares:update', args=[self.share.id])

        res = self.client.post(url, formData)

        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)
        api_manila.share_update.assert_called_once_with(
            mock.ANY, self.share, formData['name'], formData['description'],
            is_public=six.text_type(formData['is_public']))
        api_manila.share_get.assert_has_calls(
            [mock.call(mock.ANY, self.share.id) for i in (1, 2)])

    def test_list_rules(self):
        rules = [test_data.ip_rule, test_data.user_rule, test_data.cephx_rule]
        self.mock_object(
            api_manila, "share_rules_list", mock.Mock(return_value=rules))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))
        url = reverse(
            'horizon:project:shares:manage_rules', args=[self.share.id])

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'project/shares/shares/manage_rules.html')
        api_manila.share_rules_list.assert_called_once_with(
            mock.ANY, self.share.id)
        self.assertEqual(3, neutron.is_service_enabled.call_count)

    def test_create_rule(self):
        url = reverse('horizon:project:shares:rule_add', args=[self.share.id])
        self.mock_object(api_manila, "share_allow")
        formData = {
            'access_type': 'user',
            'method': u'CreateForm',
            'access_to': 'someuser',
            'access_level': 'rw',
        }

        res = self.client.post(url, formData)

        api_manila.share_allow.assert_called_once_with(
            mock.ANY, self.share.id, access_type=formData['access_type'],
            access_to=formData['access_to'],
            access_level=formData['access_level'])
        self.assertRedirectsNoFollow(
            res,
            reverse('horizon:project:shares:manage_rules',
                    args=[self.share.id])
        )

    def test_delete_rule(self):
        rule = test_data.ip_rule
        formData = {'action': 'rules__delete__%s' % rule.id}
        self.mock_object(api_manila, "share_deny")
        self.mock_object(
            api_manila, "share_rules_list", mock.Mock(return_value=[rule]))
        url = reverse(
            'horizon:project:shares:manage_rules', args=[self.share.id])

        self.client.post(url, formData)

        api_manila.share_deny.assert_called_with(
            mock.ANY, self.share.id, rule.id)
        api_manila.share_rules_list.assert_called_with(mock.ANY, self.share.id)

    def test_extend_share(self):
        formData = {'new_size': self.share.size + 1, 'method': u'UpdateForm'}
        usage_limit = {
            'maxTotalShareGigabytes': 250,
            'totalShareGigabytesUsed': 20,
        }
        url = reverse('horizon:project:shares:extend', args=[self.share.id])
        self.mock_object(api_manila, "share_extend")
        self.mock_object(
            quotas, "tenant_limit_usages", mock.Mock(return_value=usage_limit))

        response = self.client.post(url, formData)

        self.assertEqual(302, response.status_code)
        api_manila.share_extend.assert_called_once_with(
            mock.ANY, self.share.id, formData['new_size'])
