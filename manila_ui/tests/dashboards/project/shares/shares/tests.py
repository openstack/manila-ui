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

import ddt
from django.core.handlers import wsgi
from django.core.urlresolvers import reverse
import mock
import six

from horizon import messages as horizon_messages
from manila_ui.api import manila as api_manila
from manila_ui.dashboards.project.shares.shares import forms
from manila_ui.dashboards import utils
from manila_ui.tests.dashboards.project.shares import test_data
from manila_ui.tests import helpers as test

from openstack_dashboard.api import base
from openstack_dashboard.api import neutron
from openstack_dashboard.usage import quotas

SHARE_INDEX_URL = reverse('horizon:project:shares:index')


class QuotaTests(test.TestCase):

    def test_get_disabled_quotas(self):
        self.mock_object(
            base, "is_service_enabled", mock.Mock(return_value=False))

        result_quotas = quotas.get_disabled_quotas(self.request)
        expected_quotas = set(
            quotas.QUOTA_FIELDS + quotas.MISSING_QUOTA_FIELDS)

        self.assertItemsEqual(result_quotas, expected_quotas)


@ddt.ddt
class ShareViewTests(test.TestCase):

    class FakeAZ(object):
        def __init__(self, name):
            self.name = name

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

    @mock.patch.object(api_manila, 'availability_zone_list')
    def test_create_share(self, az_list):
        url = reverse('horizon:project:shares:create')
        share = test_data.share
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
        self.mock_object(
            api_manila, "share_create", mock.Mock(return_value=share))
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

    @mock.patch.object(api_manila, 'availability_zone_list')
    def test_create_share_from_snapshot(self, mock_az_list):
        share = test_data.share
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
        self.mock_object(
            api_manila, "share_create", mock.Mock(return_value=share))
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
            res, ("<div><b>Share Replica ID:</b> %s</div>" %
                  export_locations[0].share_instance_id),
            2, 200)
        for rule in rules:
            self.assertContains(res, "<dt>%s</dt>" % rule.access_type, 1, 200)
            self.assertContains(
                res, "<div><b>Access to: </b>%s</div>" % rule.access_to,
                1, 200)
            if 'cephx' == rule.access_type:
                self.assertContains(
                    res, "<div><b>Access Key: </b>%s</div>" % rule.access_key,
                    1, 200)
        self.assertContains(
            res, "<div><b>Access Key: </b></div>",
            len(rules) - sum(r.access_type == 'cephx' for r in rules), 200)
        self.assertContains(
            res, "<div><b>Access Level: </b>rw</div>", len(rules), 200)
        self.assertContains(
            res, "<div><b>Status: </b>active</div>", len(rules), 200)
        self.assertNoMessages()
        api_manila.share_rules_list.assert_called_once_with(
            mock.ANY, self.share.id)
        api_manila.share_export_location_list.assert_called_once_with(
            mock.ANY, self.share.id)

    def test_update_share_get(self):
        share = test_data.share
        url = reverse('horizon:project:shares:update', args=[share.id])
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/shares/shares/update.html')

    def test_update_share_post(self):
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
        url = reverse(
            'horizon:project:shares:manage_rules', args=[self.share.id])

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'project/shares/shares/manage_rules.html')
        api_manila.share_rules_list.assert_called_once_with(
            mock.ANY, self.share.id)

    def test_create_rule_get(self):
        url = reverse('horizon:project:shares:rule_add', args=[self.share.id])
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/shares/shares/rule_add.html')

    def test_create_rule_post(self):
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

    def test_extend_share_get(self):
        share = test_data.share
        usage_limit = {
            'maxTotalShareGigabytes': 250,
            'totalShareGigabytesUsed': 20,
        }
        url = reverse('horizon:project:shares:extend', args=[share.id])
        self.mock_object(
            quotas, "tenant_limit_usages", mock.Mock(return_value=usage_limit))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        self.assertNoMessages()
        self.assertTemplateUsed(res, 'project/shares/shares/extend.html')

    def test_extend_share_open_form_successfully(self):
        self.share.size = 5
        usage_limit = {
            'maxTotalShareGigabytes': self.share.size + 50,
            'totalShareGigabytesUsed': self.share.size,
        }
        url = reverse('horizon:project:shares:extend', args=[self.share.id])
        self.mock_object(api_manila, "share_extend")
        self.mock_object(
            quotas, "tenant_limit_usages", mock.Mock(return_value=usage_limit))

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'project/shares/shares/extend.html')
        api_manila.share_get.assert_called_once_with(mock.ANY, self.share.id)
        self.assertFalse(api_manila.share_extend.called)
        quotas.tenant_limit_usages.assert_called_once_with(mock.ANY)

    def test_extend_share_get_with_api_exception(self):
        usage_limit = {
            'maxTotalShareGigabytes': self.share.size + 50,
            'totalShareGigabytesUsed': self.share.size,
        }
        url = reverse('horizon:project:shares:extend', args=[self.share.id])
        self.mock_object(api_manila, "share_extend")
        self.mock_object(
            quotas, "tenant_limit_usages", mock.Mock(return_value=usage_limit))
        self.mock_object(
            api_manila, "share_get",
            mock.Mock(return_value=Exception('Fake share NotFound exception')))

        response = self.client.get(url)

        self.assertEqual(404, response.status_code)
        self.assertTemplateNotUsed(
            response, 'project/shares/shares/extend.html')
        self.assertFalse(api_manila.share_extend.called)
        api_manila.share_get.assert_called_once_with(mock.ANY, self.share.id)
        self.assertFalse(quotas.tenant_limit_usages.called)

    @ddt.data(6, 54, 55)
    def test_extend_share_post_successfully(self, new_size):
        self.share.size = 5
        form_data = {'new_size': new_size}
        usage_limit = {
            'maxTotalShareGigabytes': self.share.size + 50,
            'totalShareGigabytesUsed': self.share.size,
        }
        url = reverse('horizon:project:shares:extend', args=[self.share.id])
        self.mock_object(api_manila, "share_extend")
        self.mock_object(
            quotas, "tenant_limit_usages", mock.Mock(return_value=usage_limit))

        response = self.client.post(url, form_data)

        self.assertEqual(302, response.status_code)
        self.assertTemplateNotUsed(
            response, 'project/shares/shares/extend.html')
        api_manila.share_get.assert_called_once_with(mock.ANY, self.share.id)
        api_manila.share_extend.assert_called_once_with(
            mock.ANY, self.share.id, form_data['new_size'])
        quotas.tenant_limit_usages.assert_called_once_with(mock.ANY)
        self.assertRedirectsNoFollow(response, SHARE_INDEX_URL)

    @ddt.data(0, 5, 56)
    def test_extend_share_post_with_invalid_value(self, new_size):
        self.share.size = 5
        form_data = {'new_size': new_size}
        usage_limit = {
            'maxTotalShareGigabytes': self.share.size + 50,
            'totalShareGigabytesUsed': self.share.size,
        }
        url = reverse('horizon:project:shares:extend', args=[self.share.id])
        self.mock_object(api_manila, "share_extend")
        self.mock_object(
            quotas, "tenant_limit_usages", mock.Mock(return_value=usage_limit))

        response = self.client.post(url, form_data)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'project/shares/shares/extend.html')
        self.assertFalse(api_manila.share_extend.called)
        api_manila.share_get.assert_called_once_with(mock.ANY, self.share.id)
        quotas.tenant_limit_usages.assert_called_with(mock.ANY)

    def test_extend_share_post_with_api_exception(self):
        self.share.size = 5
        form_data = {'new_size': 30}
        usage_limit = {
            'maxTotalShareGigabytes': self.share.size + 50,
            'totalShareGigabytesUsed': self.share.size,
        }
        url = reverse('horizon:project:shares:extend', args=[self.share.id])
        self.mock_object(
            api_manila, "share_extend",
            mock.Mock(return_value=Exception('Fake API exception')))
        self.mock_object(
            quotas, "tenant_limit_usages", mock.Mock(return_value=usage_limit))

        response = self.client.post(url, form_data)

        self.assertEqual(302, response.status_code)
        self.assertTemplateNotUsed(
            response, 'project/shares/shares/extend.html')
        api_manila.share_extend.assert_called_once_with(
            mock.ANY, self.share.id, form_data['new_size'])
        api_manila.share_get.assert_called_once_with(mock.ANY, self.share.id)
        quotas.tenant_limit_usages.assert_called_once_with(mock.ANY)
        self.assertRedirectsNoFollow(response, SHARE_INDEX_URL)

    def test_update_share_metadata_get(self):
        share = test_data.share_with_metadata
        url = reverse(
            'horizon:project:shares:update_metadata', args=[share.id])
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.get(url)

        api_manila.share_get.assert_called_once_with(mock.ANY, share.id)
        self.assertNoMessages()
        self.assertTemplateUsed(
            res, 'project/shares/shares/update_metadata.html')

    def test_update_share_metadata_post(self):
        share = test_data.share_with_metadata
        data = {
            'metadata': 'aaa=ccc',
        }
        form_data = {
            'metadata': {'aaa': 'ccc'},
        }
        url = reverse(
            'horizon:project:shares:update_metadata', args=[share.id])
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(api_manila, "share_set_metadata")
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

        res = self.client.post(url, data)

        api_manila.share_set_metadata.assert_called_once_with(
            mock.ANY, share, form_data['metadata'])
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)


@ddt.ddt
class ShareViewFormTests(ShareViewTests, test.APITestCase):

    def setUp(self):
        super(ShareViewFormTests, self).setUp()
        FAKE_ENVIRON = {'REQUEST_METHOD': 'GET', 'wsgi.input': 'fake_input'}
        self.request = wsgi.WSGIRequest(FAKE_ENVIRON)
        self.mock_object(
            horizon_messages, "success",
            mock.Mock())

    @ddt.data((True, True), (True, False), (False, False))
    @ddt.unpack
    def test_enable_public_share_creation(self,
                                          enable_public_shares,
                                          is_public):
        def _get_form(**kwargs):
            return forms.CreateForm(self.request, **kwargs)

        self.mock_object(
            api_manila, "share_create", mock.Mock(return_value=self.share))
        self.mock_object(
            api_manila, "share_snapshot_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_manila, "share_network_list",
            mock.Mock(return_value=[test_data.active_share_network]))
        self.mock_object(
            api_manila, "share_type_list",
            mock.Mock(return_value=[self.fake_share_type, ]))
        self.mock_object(
            api_manila, "availability_zone_list",
            mock.Mock(return_value=[self.FakeAZ('fake_az'), ]))

        data = {
            'name': u'new_share',
            'description': u'This is test share',
            'method': u'CreateForm',
            'share_network': test_data.active_share_network.id,
            'size': 1,
            'share_proto': u'NFS',
            'share_type': 'fake',
            'share-network-choices-fake': test_data.active_share_network.id,
            'availability_zone': 'fake_az',
            'metadata': 'key=value',
            'snapshot_id': None,
        }
        if enable_public_shares:
            data.update({'is_public': is_public})

        with self.settings(OPENSTACK_MANILA_FEATURES={
            'enable_public_shares': enable_public_shares}):
                form = _get_form()
                result = form.handle(self.request, data)
                self.assertTrue(result)
                self.assertEqual(
                    enable_public_shares,
                    form.enable_public_shares)
                if enable_public_shares:
                    self.assertIn("is_public", form.fields)
                    self.assertTrue(form.fields["is_public"])
                else:
                    self.assertNotIn("is_public", form.fields)
                api_manila.share_create.assert_called_once_with(
                    self.request,
                    availability_zone=data['availability_zone'],
                    description=data['description'],
                    is_public=is_public,
                    metadata=utils.parse_str_meta(data['metadata'])[0],
                    name=data['name'],
                    proto=data['share_proto'],
                    share_network=test_data.active_share_network.id,
                    share_type=data['share_type'],
                    size=data['size'],
                    snapshot_id=data['snapshot_id'],
                )
                horizon_messages.success.assert_called_once_with(
                    self.request, mock.ANY)

    @ddt.data((True, True), (True, False), (False, False))
    @ddt.unpack
    def test_enable_public_share_update(self,
                                        enable_public_shares,
                                        is_public):
        def _get_form(initial):
            kwargs = {
                'prefix': None,
                'initial': initial,
            }
            return forms.UpdateForm(self.request, **kwargs)

        initial = {'share_id': 'fake_share_id'}

        self.mock_object(
            api_manila, "share_update", mock.Mock(return_value=self.share))

        data = {
            'name': u'old_share',
            'description': u'This is test share',
        }
        if enable_public_shares:
            data.update({'is_public': is_public})

        with self.settings(OPENSTACK_MANILA_FEATURES={
            'enable_public_shares': enable_public_shares}):
                form = _get_form(initial)
                result = form.handle(self.request, data)
                self.assertTrue(result)
                self.assertEqual(
                    enable_public_shares,
                    form.enable_public_shares)
                if enable_public_shares:
                    self.assertIn("is_public", form.fields)
                    self.assertTrue(form.fields["is_public"])
                else:
                    self.assertNotIn("is_public", form.fields)
                api_manila.share_update.assert_called_once_with(
                    self.request,
                    self.share,
                    data['name'],
                    data['description'],
                    is_public=is_public,
                )
                horizon_messages.success.assert_called_once_with(
                    self.request, mock.ANY)
