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

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.project.shares import test_data
from manila_ui.test import helpers as test

from openstack_dashboard import api
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

    @mock.patch.object(nova, 'availability_zone_list')
    def test_create_share(self, az_list):
        usage_limit = {'maxTotalVolumeGigabytes': 250,
                       'gigabytesUsed': 20,
                       'volumesUsed': 0,
                       'maxTotalVolumes': 6}
        share = test_data.share
        share_net = test_data.active_share_network
        share_nets = [share_net]
        formData = {'name': u'new_share',
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
        api_manila.share_create = mock.Mock(return_value=share)
        api_manila.share_snapshot_list = mock.Mock(return_value=[])
        api_manila.share_network_list = mock.Mock(return_value=share_nets)
        api_manila.share_type_list = mock.Mock(
            return_value=[self.fake_share_type, ])
        api.neutron.is_service_enabled = mock.Mock(return_value=[True])
        quotas.tenant_limit_usages = mock.Mock(return_value=[usage_limit])
        url = reverse('horizon:project:shares:create')
        self.client.post(url, formData)

        api_manila.share_create.assert_called_with(
            mock.ANY, size=formData['size'], name=formData['name'],
            description=formData['description'], proto=formData['share_proto'],
            snapshot_id=None, is_public=False, share_network=share_net.id,
            metadata={}, share_type=formData['share_type'],
            availability_zone=formData['availability_zone'])

    @mock.patch.object(nova, 'availability_zone_list')
    def test_create_share_from_snapshot(self, az_list):
        share = test_data.share
        share_net = test_data.active_share_network
        share_nets = [share_net]
        snapshot = test_data.snapshot
        formData = {'name': u'new_share',
                    'description': u'This is test share from snapshot',
                    'method': u'CreateForm',
                    'share_network': share_net.id,
                    'size': snapshot.size,
                    'share_proto': 'NFS',
                    'share_type': 'fake',
                    'share_source_type': 'snapshot',
                    'snapshot': snapshot.id,
                    'share-network-choices-fake': share_net.id,
                    'availability_zone': 'fake_az'
                    }

        az_list.return_value = [self.FakeAZ('fake_az'), ]
        api_manila.share_create = mock.Mock(return_value=share)
        api_manila.share_snapshot_list = mock.Mock(
            return_value=[snapshot])
        api_manila.share_snapshot_get = mock.Mock(
            return_value=snapshot)
        api.neutron.is_service_enabled = mock.Mock(return_value=[True])
        api_manila.share_network_list = mock.Mock(return_value=share_nets)
        api_manila.share_type_list = mock.Mock(
            return_value=[self.fake_share_type, ])

        url = reverse('horizon:project:shares:create')
        res = self.client.post(url, formData)
        api_manila.share_create.assert_called_with(
            mock.ANY, size=formData['size'], name=formData['name'],
            description=formData['description'], proto=formData['share_proto'],
            snapshot_id=snapshot.id, is_public=False,
            share_network=share_net.id, metadata={},
            share_type=formData['share_type'],
            availability_zone=formData['availability_zone'])
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)

    def test_delete_share(self):
        share = test_data.share
        api_manila.share_snapshot_list = mock.Mock(return_value=[])

        formData = {'action':
                    'shares__delete__%s' % share.id}

        api_manila.share_delete = mock.Mock()
        api_manila.share_get = mock.Mock(
            return_value=test_data.share)
        api_manila.share_list = mock.Mock(
            return_value=[test_data.share])
        url = reverse('horizon:project:shares:index')
        res = self.client.post(url, formData)
        api_manila.share_delete.assert_called_with(
            mock.ANY, test_data.share.id)

        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)

    def test_detail_view(self):
        share_net = test_data.active_share_network
        share = test_data.share
        rules = [test_data.ip_rule, test_data.user_rule]
        api_manila.share_get = mock.Mock(return_value=share)
        api_manila.share_network_get = mock.Mock(return_value=share_net)
        api_manila.share_rules_list = mock.Mock(return_value=rules)

        url = reverse('horizon:project:shares:detail',
                      args=[share.id])
        res = self.client.get(url)
        self.assertContains(res, "<h1>Share Details: %s</h1>"
                                 % share.name,
                            1, 200)

        self.assertContains(res, "<dd>%s</dd>" % share.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share.id, 1, 200)
        self.assertContains(res, "<dd>%s GiB</dd>" % share.size, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share.share_proto, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share.availability_zone, 1,
                            200)
        for rule in rules:
            self.assertContains(res, "<dt>%s</dt>" % rule.access_type,
                                1, 200)
            self.assertContains(res, "<dd>%s</dd>" % rule.access_to,
                                1, 200)
        self.assertNoMessages()

    def test_update_share(self):
        share = test_data.share

        api_manila.share_get = mock.Mock(return_value=share)
        api_manila.share_update = mock.Mock()

        formData = {'method': 'UpdateForm',
                    'name': share.name,
                    'description': share.description}

        url = reverse('horizon:project:shares:update', args=[share.id])
        res = self.client.post(url, formData)
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)

    def test_list_rules(self):
        share = test_data.share
        rules = [test_data.ip_rule, test_data.user_rule]
        api_manila.share_rules_list = mock.Mock(return_value=rules)

        url = reverse('horizon:project:shares:manage_rules', args=[share.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'project/shares/shares/manage_rules.html')

    def test_create_rule(self):
        share = test_data.share
        url = reverse('horizon:project:shares:rule_add', args=[share.id])
        api_manila.share_get = mock.Mock(return_value=share)
        api_manila.share_allow = mock.Mock()
        api.neutron.is_service_enabled = mock.Mock(return_value=[True])
        formData = {'access_type': 'user',
                    'method': u'CreateForm',
                    'access_to': 'someuser',
                    'access_level': 'rw'}
        res = self.client.post(url, formData)
        api_manila.share_allow.assert_called_once_with(
            mock.ANY, share.id, access_type=formData['access_type'],
            access_to=formData['access_to'],
            access_level=formData['access_level'])
        self.assertRedirectsNoFollow(
            res,
            reverse('horizon:project:shares:manage_rules', args=[share.id]))

    def test_delete_rule(self):
        rule = test_data.ip_rule
        share = test_data.share
        formData = {'action':
                    'rules__delete__%s' % rule.id}

        api_manila.share_deny = mock.Mock()
        api_manila.share_get = mock.Mock(
            return_value=test_data.share)
        api_manila.share_rules_list = mock.Mock(
            return_value=[rule])
        url = reverse('horizon:project:shares:manage_rules', args=[share.id])
        self.client.post(url, formData)
        api_manila.share_deny.assert_called_with(
            mock.ANY, test_data.share.id, rule.id)

    def test_extend_share(self):
        share = test_data.share
        formData = {'new_size': share.size + 1,
                    'method': u'UpdateForm'}
        usage_limit = {'maxTotalShareGigabytes': 250,
                       'totalShareGigabytesUsed': 20}
        url = reverse('horizon:project:shares:extend', args=[share.id])

        api_manila.share_get = mock.Mock(return_value=share)
        quotas.tenant_limit_usages = mock.Mock(return_value=usage_limit)
        share_extend = mock.Mock()

        with mock.patch('manila_ui.api.manila.share_extend', share_extend):
            response = self.client.post(url, formData)

            self.assertEqual(302, response.status_code)
            share_extend.assert_called_once_with(
                mock.ANY, share.id, formData['new_size'])
