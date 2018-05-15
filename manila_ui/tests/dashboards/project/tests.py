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

from django.urls import reverse
from django.utils import translation
import mock

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
