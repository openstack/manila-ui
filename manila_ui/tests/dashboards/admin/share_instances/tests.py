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
from manila_ui.tests.dashboards.project import test_data
from manila_ui.tests import helpers as test

INDEX_URL = reverse('horizon:admin:share_instances:index')


class ShareInstanceTests(test.BaseAdminViewTests):

    def test_list_share_instances(self):
        share_instances = [
            test_data.share_instance,
            test_data.share_instance_no_ss,
        ]
        self.mock_object(
            api_manila, "share_instance_list",
            mock.Mock(return_value=share_instances))
        self.mock_object(
            api_keystone, "tenant_list", mock.Mock(return_value=([], None)))

        res = self.client.get(INDEX_URL)

        self.assertContains(res, "<h1>Share Instances</h1>")
        self.assertContains(
            res,
            '<a href="/admin/share_servers/%s" >%s</a>' % (
                share_instances[0].share_server_id,
                share_instances[0].share_server_id),
            1, 200)
        self.assertContains(
            res,
            '<a href="/admin/share_networks/%s" >%s</a>' % (
                share_instances[0].share_network_id,
                share_instances[0].share_network_id),
            1, 200)
        for si in share_instances:
            self.assertContains(
                res, '<a href="/admin/share_instances/%s" >%s</a>' % (
                    si.id, si.id))
            self.assertContains(res, si.host)
            self.assertContains(res, si.availability_zone)
            self.assertContains(
                res,
                '<a href="/admin/shares/%s/" >%s</a>' % (
                    si.share_id, si.share_id),
                1, 200)
        api_manila.share_instance_list.assert_called_once_with(mock.ANY)
        self.assertEqual(0, api_keystone.tenant_list.call_count)

    def test_detail_view_share_instance(self):
        share_instance = test_data.share_instance
        share_id = share_instance.share_id
        ss_id = share_instance.share_server_id
        url = reverse('horizon:admin:share_instances:share_instance_detail',
                      args=[share_instance.id])
        self.mock_object(
            api_manila, "share_instance_get",
            mock.Mock(return_value=share_instance))
        self.mock_object(
            api_manila, "share_instance_export_location_list",
            mock.Mock(return_value=test_data.export_locations))

        res = self.client.get(url)

        self.assertContains(
            res, "<h1>Share Instance Details: %s</h1>" % share_instance.id,
            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_instance.id, 1, 200)
        self.assertContains(res, "<dd>Available</dd>", 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_instance.host, 1, 200)
        self.assertContains(
            res, "<dd>%s</dd>" % share_instance.availability_zone, 1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/shares/%s/\">%s</a></dd>" % (
                share_id, share_id),
            1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/share_networks/%s\">%s</a></dd>" % (
                share_instance.share_network_id,
                share_instance.share_network_id),
            1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/share_servers/%s\">%s</a></dd>" % (
                ss_id, ss_id),
            1, 200)
        self.assertNoMessages()
        api_manila.share_instance_get.assert_called_once_with(
            mock.ANY, share_instance.id)
        api_manila.share_instance_export_location_list.assert_called_once_with(
            mock.ANY, share_instance.id)

    def test_detail_view_share_instance_with_exception(self):
        share_instance = test_data.share_instance
        url = reverse('horizon:admin:share_instances:share_instance_detail',
                      args=[share_instance.id])
        self.mock_object(
            api_manila, "share_instance_get",
            mock.Mock(side_effect=horizon_exceptions.NotFound(404)))

        res = self.client.get(url)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_instance_get.assert_called_once_with(
            mock.ANY, share_instance.id)
