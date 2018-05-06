# Copyright (c) 2014 NetApp, Inc.
# Copyright (c) 2015 Mirantis, Inc.
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
from horizon import exceptions as horizon_exceptions
import mock
from openstack_dashboard.api import keystone as api_keystone

from manila_ui.api import manila as api_manila
from manila_ui.dashboards.admin import utils
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test
from manila_ui.tests.test_data import keystone_data

INDEX_URL = reverse('horizon:admin:share_snapshots:index')


class SnapshotsTests(test.BaseAdminViewTests):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(keystone_data.projects, None)))
        # Reset taken list of projects to avoid test interference
        utils.PROJECTS = {}

    def test_detail_view(self):
        snapshot = test_data.snapshot
        share = test_data.share
        url = reverse('horizon:admin:share_snapshots:share_snapshot_detail',
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
        rules = [test_data.ip_rule, test_data.user_rule, test_data.cephx_rule]
        export_locations = test_data.admin_snapshot_export_locations
        share = test_data.share_mount_snapshot
        url = reverse('horizon:admin:share_snapshots:share_snapshot_detail',
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
            self.assertContains(
                res, "<div><b>Is admin only:</b> %s</div>" % el.is_admin_only,
                1, 200)
            self.assertContains(
                res, ("<div><b>Snapshot Replica ID:</b> %s</div>" %
                      el.share_snapshot_instance_id), 1, 200)
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

    def test_detail_view_with_exception(self):
        url = reverse('horizon:admin:share_snapshots:share_snapshot_detail',
                      args=[test_data.snapshot.id])
        self.mock_object(
            api_manila, "share_snapshot_get",
            mock.Mock(side_effect=horizon_exceptions.NotFound(404)))

        res = self.client.get(url)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_snapshot_get.assert_called_once_with(
            mock.ANY, test_data.snapshot.id)

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

        api_keystone.tenant_list.assert_called_once_with(mock.ANY)
        api_manila.share_snapshot_delete.assert_called_once_with(
            mock.ANY, test_data.snapshot.id)
        api_manila.share_snapshot_list.assert_called_once_with(
            mock.ANY, search_opts={'all_tenants': True})
        api_manila.share_list.assert_called_once_with(mock.ANY)
        self.assertRedirectsNoFollow(res, INDEX_URL)
