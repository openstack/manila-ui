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
from django.core.urlresolvers import reverse
from django.utils import translation
import mock

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.project import shares
from manila_ui.tests.dashboards.project.shares import test_data
from manila_ui.tests import helpers as test

from openstack_dashboard.api import neutron as api_neutron
from openstack_dashboard.usage import quotas

INDEX_URL = reverse('horizon:project:shares:index')


class SharesTests(test.TestCase):

    def test_index_with_all_tabs(self):
        snaps = [test_data.snapshot]
        shares = [test_data.share, test_data.nameless_share,
                  test_data.other_share]
        share_networks = [test_data.inactive_share_network,
                          test_data.active_share_network]
        security_services = [test_data.sec_service]
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=shares))
        self.mock_object(
            api_manila, "share_snapshot_list", mock.Mock(return_value=snaps))
        self.mock_object(
            api_manila, "share_network_list",
            mock.Mock(return_value=share_networks))
        self.mock_object(
            api_manila, "security_service_list",
            mock.Mock(return_value=security_services))
        self.mock_object(
            api_neutron, "is_service_enabled", mock.Mock(return_value=[True]))
        self.mock_object(
            api_neutron, "network_list", mock.Mock(return_value=[]))
        self.mock_object(
            api_neutron, "subnet_list", mock.Mock(return_value=[]))
        self.mock_object(
            quotas, "tenant_limit_usages",
            mock.Mock(return_value=test_data.quota_usage))
        self.mock_object(
            quotas, "tenant_quota_usages",
            mock.Mock(return_value=test_data.quota_usage))

        res = self.client.get(INDEX_URL)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'project/shares/index.html')
        api_neutron.network_list.assert_called_once_with(mock.ANY)
        api_neutron.subnet_list.assert_called_once_with(mock.ANY)
        api_manila.security_service_list.assert_called_once_with(mock.ANY)
        api_manila.share_snapshot_list.assert_called_with(mock.ANY)
        api_manila.share_list.assert_called_with(mock.ANY)
        api_manila.share_network_list.assert_has_calls([
            mock.call(mock.ANY),
            mock.call(mock.ANY, detailed=True),
        ], any_order=True)


class PieChartsTests(test.TestCase):

    def test_get_context_data(self):
        limits = {
            "totalSharesUsed": 1,
            "totalShareGigabytesUsed": 2,
            "totalShareNetworksUsed": 3,
            "totalShareSnapshotsUsed": 4,
            "totalSnapshotGigabytesUsed": 5,
            "maxTotalShares": 6,
            "maxTotalShareGigabytes": 7,
            "maxTotalShareNetworks": 8,
            "maxTotalShareSnapshots": 9,
            "maxTotalSnapshotGigabytes": 10,
        }
        existing_chart_name = "Foo"
        existing_chart = {
            "name": translation.ugettext_lazy(existing_chart_name),
            "used": 11,
            "max": 13,
            "text": "fake_text",
        }

        class ParentViewInstance(mock.MagicMock):
            def get_context_data(self, **kwargs):
                return {"charts": [existing_chart]}

        class ViewInstance(ParentViewInstance):
            usage = type("FakeUsage", (object, ), {"limits": limits})

        view_instance = ViewInstance()

        result = shares.get_context_data(
            view_instance, fook="foov", bark="barv")

        charts = result.get("charts", [])
        self.assertEqual(6, len(charts))
        expected_charts = {
            existing_chart_name: {
                "name": existing_chart_name, "used": existing_chart["used"],
                "max": existing_chart["max"], "text": existing_chart["text"]},
            "Shares": {"name": "Shares", "used": 1, "max": 6, "text": False},
            "Share Storage": {
                "name": "Share Storage", 'used': 2, "max": 7, "text": False},
            "Share Networks": {
                "name": "Share Networks", "used": 3, "max": 8, "text": False},
            "Share Snapshots": {
                "name": "Share Snapshots", "used": 4, "max": 9, "text": False},
            "Share Snapshots Storage": {
                "name": "Share Snapshots Storage", "used": 5, "max": 10,
                "text": False},
        }
        for chart in charts:
            name = chart["name"].title()
            self.assertEqual(
                {"name": name, "used": chart["used"], "max": chart["max"],
                 "text": chart["text"]},
                expected_charts.pop(name, "NotFound")
            )


@ddt.ddt
class QuotaTests(test.TestCase):

    @ddt.data(
        shares.ManilaUpdateDefaultQuotaAction,
        shares.ManilaUpdateProjectQuotaAction,
        shares.ManilaCreateProjectQuotaAction,
    )
    def test_manila_quota_action(self, class_ref):
        self.mock_object(
            quotas, 'get_disabled_quotas', mock.Mock(return_value=[]))
        class_instance = class_ref(self.request, 'foo')
        expected_fields = set([
            'shares', 'share_gigabytes', 'share_snapshots',
            'share_snapshot_gigabytes', 'share_networks',
        ])
        # NOTE(vponomaryov): iterate over reversed list of visible fields
        # because manila's fields are at the end always.
        for vf in reversed(class_instance.visible_fields()):
            if expected_fields and vf.name in expected_fields:
                self.assertEqual(-1, vf.field.min_value)
                self.assertIsInstance(
                    vf.field, shares.horizon.forms.IntegerField)
                expected_fields.remove(vf.name)
        self.assertSetEqual(set([]), expected_fields)
        self.assertTrue(quotas.get_disabled_quotas.called)

    @ddt.data('default_quota_get', 'tenant_quota_get')
    def test__get_manila_quota_data(self, method_name):
        fake_quotas = [
            type('Fake', (object, ), {'name': name})
            for name in ('gigabytes', 'snapshots', 'snapshot_gigabytes')
        ]
        self.mock_object(
            api_manila, method_name, mock.Mock(return_value=fake_quotas))
        self.mock_object(
            shares, '_get_manila_disabled_quotas',
            mock.Mock(return_value=[]))

        result = shares._get_manila_quota_data(
            self.request, method_name)

        expected = [
            'share_gigabytes',
            'share_snapshot_gigabytes',
            'share_snapshots',
        ]
        self.assertEqual(3, len(result))
        self.assertEqual(
            expected,
            sorted([element.name for element in result]))
        getattr(api_manila, method_name).assert_called_once_with(
            self.request, self.request.user.tenant_id)
        shares._get_manila_disabled_quotas.asssert_called_once_with(
            self.request)

    def test_manila_quota_fields(self):
        expected_fields = (
            "shares",
            "share_gigabytes",
            "share_snapshots",
            "share_snapshot_gigabytes",
            "share_networks",
        )
        for ef in expected_fields:
            self.assertIn(ef, shares.quotas.QUOTA_FIELDS)
