# Copyright (c) 2016 Mirantis, Inc.
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
import mock
from openstack_dashboard.api import neutron

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.project.shares.replicas import tables as r_tables
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:project:shares:index')


class FakeAZ(object):
    def __init__(self, name):
        self.name = name


@ddt.ddt
class ReplicasTests(test.TestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.share = test_data.share
        self.share_replica = test_data.share_replica
        self.share_replica2 = test_data.share_replica2
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=self.share))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

    def test_create_get(self):
        url = reverse(
            "horizon:project:shares:create_replica", args=[self.share.id])
        old_az = self.share.availability_zone
        new_az = old_az + "_new"
        self.mock_object(api_manila, "share_replica_create")
        self.mock_object(
            api_manila, "availability_zone_list",
            mock.Mock(return_value=[FakeAZ(new_az), FakeAZ(old_az)]))

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertFalse(api_manila.share_replica_create.called)
        api_manila.availability_zone_list.assert_called_once_with(mock.ANY)
        self.assertNoMessages()
        self.assertTemplateUsed(
            res, "project/shares/replicas/create_replica.html")

    def _create_post(self):
        url = reverse(
            "horizon:project:shares:create_replica", args=[self.share.id])
        old_az = self.share.availability_zone
        new_az = old_az + "_new"
        formData = {
            "share_id": self.share.id,
            "availability_zone": new_az,
        }
        self.mock_object(
            api_manila, "availability_zone_list",
            mock.Mock(return_value=[FakeAZ(new_az), FakeAZ(old_az)]))
        self.mock_object(
            api_manila,
            "share_replica_create",
            mock.Mock(return_value=test_data.share_replica))

        res = self.client.post(url, formData)

        self.assertEqual(302, res.status_code)
        api_manila.share_replica_create.assert_called_once_with(
            mock.ANY, self.share.id, formData["availability_zone"])
        api_manila.share_replica_create.assert_called_once_with(
            mock.ANY, formData["share_id"], formData["availability_zone"])
        api_manila.availability_zone_list.assert_called_once_with(mock.ANY)
        self.assertRedirectsNoFollow(
            res,
            reverse("horizon:project:shares:manage_replicas",
                    args=[self.share.id]))

    def test_create_post(self):
        self.mock_object(api_manila, "share_replica_create")
        self._create_post()

    def test_create_post_error(self):
        self.mock_object(
            api_manila,
            "share_replica_create",
            mock.Mock(side_effect=Exception("Fake exception")))
        self._create_post()

    @ddt.data(True, False)
    def test_detail_with_export_locations_available(self, exports_available):
        url = reverse(
            "horizon:project:shares:replica_detail",
            args=[self.share_replica.id])

        export_locations_call_behavior = (
            {'return_value': test_data.export_locations} if exports_available
            else {'side_effect': Exception("Access denied to this resource")}
        )
        self.mock_object(
            api_manila, "share_replica_get",
            mock.Mock(return_value=self.share_replica))
        self.mock_object(
            api_manila, "share_instance_export_location_list",
            mock.Mock(**export_locations_call_behavior))

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(res, "project/shares/replicas/detail.html")
        self.assertNoMessages()
        self.assertContains(res, "<h3>Share Replica Overview", 1, 200)
        self.assertContains(res, ">%s</a>" % self.share.id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % self.share_replica.id, 1, 200)
        self.assertContains(
            res, "<dd>%s</dd>" % self.share.availability_zone, 1, 200)
        if exports_available:
            for el in test_data.export_locations:
                self.assertContains(res, "value=\"%s\"" % el.path, 1, 200)
                self.assertContains(
                    res, "<div><b>Preferred:</b> %s</div>" % el.preferred,
                    1, 200)
            self.assertContains(
                res, "<div><b>Is admin only:</b> %s</div>" % el.is_admin_only,
                1, 200)
        self.assertNoMessages()
        api_manila.share_replica_get.assert_called_once_with(
            mock.ANY, self.share_replica.id)
        api_manila.share_instance_export_location_list.assert_called_once_with(
            mock.ANY, self.share_replica.id)

    def test_detail_not_found(self):
        url = reverse("horizon:project:shares:replica_detail",
                      args=[self.share_replica.id])
        self.mock_object(
            api_manila,
            "share_replica_get",
            mock.Mock(
                side_effect=Exception("Fake replica NotFound exception")))
        self.mock_object(api_manila, "share_instance_export_location_list")

        res = self.client.get(url)

        self.assertEqual(302, res.status_code)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertTemplateNotUsed(res, "project/shares/replicas/detail.html")
        api_manila.share_replica_get.assert_called_once_with(
            mock.ANY, self.share_replica.id)
        self.assertFalse(api_manila.share_instance_export_location_list.called)

    def test_list(self):
        self.mock_object(
            api_manila,
            "share_replica_list",
            mock.Mock(return_value=[self.share_replica]))
        url = reverse(
            "horizon:project:shares:manage_replicas", args=[self.share.id])

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(
            res, "project/shares/replicas/manage_replicas.html")
        api_manila.share_get.assert_called_with(mock.ANY, self.share.id)
        api_manila.share_replica_list.assert_called_with(
            mock.ANY, self.share.id)

    def test_list_exception(self):
        self.mock_object(
            api_manila,
            "share_replica_list",
            mock.Mock(side_effect=Exception("Fake exception")))
        url = reverse(
            "horizon:project:shares:manage_replicas", args=[self.share.id])

        res = self.client.get(url)

        self.assertEqual(302, res.status_code)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        self.assertTemplateNotUsed(
            res, "project/shares/replicas/manage_replicas.html")
        api_manila.share_replica_list.assert_called_with(
            mock.ANY, self.share.id)

    @ddt.data(
        ([test_data.share_replica], test_data.share_replica.id, None),
        ([test_data.share_replica], test_data.share_replica.id, 'dr'),
        ([test_data.share_replica], test_data.share_replica.id, 'readable'),
        ([test_data.share_replica], test_data.share_replica.id, 'writable'),
        ([test_data.share_replica, test_data.share_replica2],
         test_data.share_replica.id, 'dr'),
        ([test_data.share_replica, test_data.share_replica2],
         test_data.share_replica.id, 'readable'),
    )
    @ddt.unpack
    def test_delete_not_allowed(self, replica_list, replica_id,
                                replication_type):
        share = test_data.share
        share.replication_type = replication_type
        formData = {"action": "replicas__delete__%s" % replica_id}
        self.mock_object(api_manila, "share_replica_delete")
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(
            api_manila,
            "share_replica_list",
            mock.Mock(return_value=replica_list))
        url = reverse(
            "horizon:project:shares:manage_replicas", args=[share.id])

        res = self.client.post(url, formData)

        self.assertEqual(302, res.status_code)
        self.assertRedirectsNoFollow(res, url)
        api_manila.share_replica_list.assert_called_with(mock.ANY, share.id)
        self.assertFalse(api_manila.share_replica_delete.called)

    @ddt.data(
        ([test_data.share_replica, test_data.share_replica2],
         test_data.share_replica2.id, 'dr'),
        ([test_data.share_replica, test_data.share_replica2],
         test_data.share_replica2.id, 'readable'),
        ([test_data.share_replica, test_data.share_replica3],
         test_data.share_replica.id, 'writable'),
        ([test_data.share_replica, test_data.share_replica3],
         test_data.share_replica3.id, 'writable'),
    )
    @ddt.unpack
    def test_delete_allowed(self, replica_list, replica_id, replication_type):
        share = test_data.share
        share.replication_type = replication_type
        formData = {"action": "replicas__delete__%s" % replica_id}
        self.mock_object(api_manila, "share_replica_delete")
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=share))
        self.mock_object(
            api_manila,
            "share_replica_list", mock.Mock(return_value=replica_list))
        url = reverse(
            "horizon:project:shares:manage_replicas", args=[share.id])

        res = self.client.post(url, formData)

        self.assertEqual(302, res.status_code)
        self.assertRedirectsNoFollow(res, url)
        api_manila.share_replica_list.assert_called_with(mock.ANY, share.id)
        api_manila.share_replica_delete.assert_called_with(
            mock.ANY, replica_id)

    def test_set_as_active_get(self):
        url = reverse(
            "horizon:project:shares:set_replica_as_active",
            args=[self.share_replica.id])
        self.mock_object(api_manila, "share_replica_get")
        self.mock_object(api_manila, "share_replica_promote")

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(
            res, "project/shares/replicas/set_replica_as_active.html")
        self.assertFalse(api_manila.share_replica_get.called)
        self.assertFalse(api_manila.share_replica_promote.called)

    def _set_as_active_post(self):
        url = reverse(
            "horizon:project:shares:set_replica_as_active",
            args=[self.share_replica.id])
        self.mock_object(
            api_manila,
            "share_replica_get",
            mock.Mock(return_value=self.share_replica))
        formData = {"replica_id": self.share_replica.id}

        res = self.client.post(url, formData)

        self.assertEqual(302, res.status_code)
        self.assertTemplateNotUsed(
            res, "project/shares/replicas/set_replica_as_active.html")
        api_manila.share_replica_promote.assert_called_once_with(
            mock.ANY, self.share_replica)
        return res

    def test_set_as_active_post(self):
        self.mock_object(api_manila, "share_replica_promote")

        res = self._set_as_active_post()

        self.assertRedirectsNoFollow(
            res,
            reverse("horizon:project:shares:manage_replicas",
                    args=[self.share.id]))

    def test_set_as_active_post_error(self):
        self.mock_object(
            api_manila,
            "share_replica_promote",
            mock.Mock(side_effect=Exception("Fake exception")))

        res = self._set_as_active_post()

        self.assertRedirectsNoFollow(
            res, reverse("horizon:project:shares:index"))

    def test_replicas_table(self):
        replicas_table = r_tables.ReplicasTable(self.request)
        counter = 0
        columns = ['created_at', 'updated_at']
        for column in replicas_table.get_columns():
            if column.name in columns:
                self.assertEqual(1, len(column.filters))
                self.assertEqual(
                    column.filters[0], r_tables.filters.parse_isotime)
                counter += 1
                columns.remove(column.name)
        self.assertEqual(
            2, counter,
            "The following columns are missing: %s." % ', '.join(columns))
