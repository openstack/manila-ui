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
from openstack_dashboard.api import base
from openstack_dashboard.usage import quotas

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.project import shares
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:project:shares:index')


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

    def test_get_disabled_quotas(self):
        self.mock_object(
            base, "is_service_enabled", mock.Mock(return_value=False))

        result_quotas = quotas.get_disabled_quotas(self.request)

        expected_quotas = set(quotas.QUOTA_FIELDS)
        self.assertItemsEqual(result_quotas, expected_quotas)

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
