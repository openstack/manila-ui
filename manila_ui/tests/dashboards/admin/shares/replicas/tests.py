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

from manila_ui.api import manila as api_manila
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

from openstack_dashboard.api import neutron

SHARE_INDEX_URL = reverse('horizon:admin:shares:index')


@ddt.ddt
class ReplicasTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.share = test_data.share
        self.share_replica = test_data.share_replica
        self.share_replica2 = test_data.share_replica2
        self.mock_object(
            api_manila, "share_get", mock.Mock(return_value=self.share))
        self.mock_object(
            neutron, "is_service_enabled", mock.Mock(return_value=[True]))

    def test_detail(self):
        url = reverse(
            "horizon:admin:shares:replica_detail",
            args=[self.share_replica.id])
        export_locations = test_data.export_locations
        self.mock_object(
            api_manila, "share_replica_get",
            mock.Mock(return_value=self.share_replica))
        self.mock_object(
            api_manila, "share_instance_export_location_list",
            mock.Mock(return_value=export_locations))

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(res, "admin/shares/replicas/detail.html")
        self.assertNoMessages()
        self.assertContains(res, "<h3>Share Replica Overview", 1, 200)
        self.assertContains(res, ">%s</a>" % self.share.id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % self.share_replica.id, 1, 200)
        self.assertContains(
            res, "<dd>%s</dd>" % self.share.availability_zone, 1, 200)
        for el in export_locations:
            self.assertContains(res, "value=\"%s\"" % el.path, 1, 200)
            self.assertContains(
                res, "<div><b>Preferred:</b> %s</div>" % el.preferred, 1, 200)
            self.assertContains(
                res, "<div><b>Is admin only:</b> %s</div>" % el.is_admin_only,
                1, 200)
        self.assertNoMessages()
        api_manila.share_replica_get.assert_called_once_with(
            mock.ANY, self.share_replica.id)
        api_manila.share_instance_export_location_list.assert_called_once_with(
            mock.ANY, self.share_replica.id)

    def test_detail_not_found(self):
        url = reverse("horizon:admin:shares:replica_detail",
                      args=[self.share_replica.id])
        self.mock_object(
            api_manila,
            "share_replica_get",
            mock.Mock(
                side_effect=Exception("Fake replica NotFound exception")))
        self.mock_object(api_manila, "share_instance_export_location_list")

        res = self.client.get(url)

        self.assertEqual(302, res.status_code)
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)
        self.assertTemplateNotUsed(res, "admin/shares/replicas/detail.html")
        api_manila.share_replica_get.assert_called_once_with(
            mock.ANY, self.share_replica.id)
        self.assertFalse(api_manila.share_instance_export_location_list.called)

    def test_list(self):
        self.mock_object(
            api_manila,
            "share_replica_list",
            mock.Mock(return_value=[self.share_replica]))
        url = reverse(
            "horizon:admin:shares:manage_replicas", args=[self.share.id])

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(
            res, "admin/shares/replicas/manage_replicas.html")
        api_manila.share_get.assert_called_with(mock.ANY, self.share.id)
        api_manila.share_replica_list.assert_called_with(
            mock.ANY, self.share.id)

    def test_list_exception(self):
        self.mock_object(
            api_manila,
            "share_replica_list",
            mock.Mock(side_effect=Exception("Fake exception")))
        url = reverse(
            "horizon:admin:shares:manage_replicas", args=[self.share.id])

        res = self.client.get(url)

        self.assertEqual(302, res.status_code)
        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)
        self.assertTemplateNotUsed(
            res, "admin/shares/replicas/manage_replicas.html")
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
            "horizon:admin:shares:manage_replicas", args=[share.id])

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
            "horizon:admin:shares:manage_replicas", args=[share.id])

        res = self.client.post(url, formData)

        self.assertEqual(302, res.status_code)
        self.assertRedirectsNoFollow(res, url)
        api_manila.share_replica_list.assert_called_with(mock.ANY, share.id)
        api_manila.share_replica_delete.assert_called_with(
            mock.ANY, replica_id)

    def test_resync_replica_get(self):
        url = reverse(
            "horizon:admin:shares:resync_replica",
            args=[self.share_replica.id])
        self.mock_object(api_manila, "share_replica_get")
        self.mock_object(api_manila, "share_replica_resync")

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(
            res, "admin/shares/replicas/resync_replica.html")
        self.assertFalse(api_manila.share_replica_get.called)
        self.assertFalse(api_manila.share_replica_resync.called)

    def _resync_post(self):
        url = reverse(
            "horizon:admin:shares:resync_replica",
            args=[self.share_replica.id])
        self.mock_object(
            api_manila,
            "share_replica_get",
            mock.Mock(return_value=self.share_replica))
        formData = {
            "method": "ResyncReplicaForm",
            "replica_id": self.share_replica.id,
        }

        res = self.client.post(url, formData)

        self.assertEqual(302, res.status_code)
        self.assertTemplateNotUsed(
            res, "admin/shares/replicas/resync_replica.html")
        api_manila.share_replica_resync.assert_called_once_with(
            mock.ANY, self.share_replica)
        return res

    def test_resync_post(self):
        self.mock_object(api_manila, "share_replica_resync")

        res = self._resync_post()

        self.assertRedirectsNoFollow(
            res,
            reverse("horizon:admin:shares:manage_replicas",
                    args=[self.share.id]))

    def test_resync_post_error(self):
        self.mock_object(
            api_manila,
            "share_replica_resync",
            mock.Mock(side_effect=Exception("Fake exception")))

        res = self._resync_post()

        self.assertRedirectsNoFollow(
            res, reverse("horizon:admin:shares:index"))

    def test_reset_replica_status_get(self):
        url = reverse(
            "horizon:admin:shares:reset_replica_status",
            args=[self.share_replica.id])
        self.mock_object(api_manila, "share_replica_get")
        self.mock_object(api_manila, "share_replica_reset_status")

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(
            res, "admin/shares/replicas/reset_replica_status.html")
        self.assertFalse(api_manila.share_replica_get.called)
        self.assertFalse(api_manila.share_replica_reset_status.called)

    @ddt.data("available", "creating", "deleting", "error")
    def test_reset_replica_status_post(self, status):
        url = reverse(
            "horizon:admin:shares:reset_replica_status",
            args=[self.share_replica.id])
        self.mock_object(
            api_manila, "share_replica_get",
            mock.Mock(return_value=self.share_replica))
        self.mock_object(api_manila, "share_replica_reset_status")
        form_data = {"replica_status": status}

        res = self.client.post(url, form_data)

        self.assertEqual(302, res.status_code)
        self.assertTemplateNotUsed(
            res, "admin/shares/replicas/reset_replica_status.html")
        api_manila.share_replica_reset_status.assert_called_once_with(
            mock.ANY, self.share_replica, status)
        self.assertRedirectsNoFollow(
            res,
            reverse("horizon:admin:shares:manage_replicas",
                    args=[self.share.id]))

    def test_reset_replica_status_error(self):
        status = "error"
        url = reverse(
            "horizon:admin:shares:reset_replica_status",
            args=[self.share_replica.id])
        self.mock_object(
            api_manila, "share_replica_get",
            mock.Mock(return_value=self.share_replica))
        self.mock_object(
            api_manila,
            "share_replica_reset_status",
            mock.Mock(side_effect=Exception("Fake exception")))
        form_data = {"replica_status": status}

        res = self.client.post(url, form_data)

        self.assertEqual(302, res.status_code)
        self.assertTemplateNotUsed(
            res, "admin/shares/replicas/reset_replica_status.html")
        api_manila.share_replica_reset_status.assert_called_once_with(
            mock.ANY, self.share_replica, status)
        self.assertRedirectsNoFollow(
            res, reverse("horizon:admin:shares:index"))

    def test_reset_replica_state_get(self):
        url = reverse(
            "horizon:admin:shares:reset_replica_state",
            args=[self.share_replica.id])
        self.mock_object(api_manila, "share_replica_get")
        self.mock_object(api_manila, "share_replica_reset_state")

        res = self.client.get(url)

        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(
            res, "admin/shares/replicas/reset_replica_state.html")
        self.assertFalse(api_manila.share_replica_get.called)
        self.assertFalse(api_manila.share_replica_reset_state.called)

    @ddt.data("active", "in_sync", "out_of_sync", "error")
    def test_reset_replica_state_post(self, state):
        url = reverse(
            "horizon:admin:shares:reset_replica_state",
            args=[self.share_replica.id])
        self.mock_object(
            api_manila, "share_replica_get",
            mock.Mock(return_value=self.share_replica))
        self.mock_object(api_manila, "share_replica_reset_state")
        form_data = {"replica_state": state}

        res = self.client.post(url, form_data)

        self.assertEqual(302, res.status_code)
        self.assertTemplateNotUsed(
            res, "admin/shares/replicas/reset_replica_state.html")
        api_manila.share_replica_reset_state.assert_called_once_with(
            mock.ANY, self.share_replica, state)
        self.assertRedirectsNoFollow(
            res,
            reverse("horizon:admin:shares:manage_replicas",
                    args=[self.share.id]))

    def test_reset_replica_state_error(self):
        state = "error"
        url = reverse(
            "horizon:admin:shares:reset_replica_state",
            args=[self.share_replica.id])
        self.mock_object(
            api_manila, "share_replica_get",
            mock.Mock(return_value=self.share_replica))
        self.mock_object(
            api_manila,
            "share_replica_reset_state",
            mock.Mock(side_effect=Exception("Fake exception")))
        form_data = {"replica_state": state}

        res = self.client.post(url, form_data)

        self.assertEqual(302, res.status_code)
        self.assertTemplateNotUsed(
            res, "admin/shares/replicas/reset_replica_state.html")
        api_manila.share_replica_reset_state.assert_called_once_with(
            mock.ANY, self.share_replica, state)
        self.assertRedirectsNoFollow(
            res, reverse("horizon:admin:shares:index"))
