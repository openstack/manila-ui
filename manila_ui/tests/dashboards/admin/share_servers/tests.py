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

INDEX_URL = reverse('horizon:admin:share_servers:index')


class ShareServerTests(test.BaseAdminViewTests):

    def test_list_share_servers(self):
        share_servers = [
            test_data.share_server,
            test_data.share_server_errored,
        ]
        projects = [
            type('FakeProject', (object, ),
                 {'id': s.project_id, 'name': '%s_name' % s.project_id})
            for s in share_servers
        ]
        projects_dict = {p.id: p for p in projects}
        self.mock_object(
            api_manila, "share_server_list",
            mock.Mock(return_value=share_servers))
        self.mock_object(
            api_manila, "share_list",
            mock.Mock(side_effect=[
                [], [test_data.share], [test_data.nameless_share]]))
        self.mock_object(
            api_keystone, "tenant_list",
            mock.Mock(return_value=(projects, None)))

        res = self.client.get(INDEX_URL)

        self.assertContains(res, "<h1>Share Servers</h1>")
        for share_server in share_servers:
            self.assertContains(
                res,
                '<a href="/admin/share_servers/%s" >%s</a>' % (
                    share_server.id, share_server.id),
                1, 200)
            self.assertContains(res, share_server.host, 1, 200)
            self.assertContains(
                res, projects_dict[share_server.project_id].name, 1, 200)
            self.assertContains(
                res,
                '<a href="/admin/share_networks/%s" >%s</a>' % (
                    share_server.share_network_id,
                    share_server.share_network),
                1, 200)
        api_manila.share_list.assert_has_calls([
            mock.call(
                mock.ANY, search_opts={'share_server_id': share_server.id})
            for share_server in share_servers
        ])
        api_manila.share_server_list.assert_called_once_with(mock.ANY)
        self.assertEqual(1, api_keystone.tenant_list.call_count)

    def test_detail_view_share_server(self):
        share_server = test_data.share_server
        shares = [test_data.share, test_data.nameless_share]
        url = reverse(
            'horizon:admin:share_servers:share_server_detail',
            args=[share_server.id])
        self.mock_object(
            api_manila, "share_server_get",
            mock.Mock(return_value=share_server))
        self.mock_object(
            api_manila, "share_list", mock.Mock(return_value=shares))

        res = self.client.get(url)

        self.assertContains(
            res, "<h1>Share Server Details: %s</h1>" % share_server.id,
            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_server.id, 1, 200)
        self.assertContains(res, "<dd>Active</dd>", 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % share_server.host, 1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/share_networks/%s\">%s</a></dd>" % (
                share_server.share_network_id,
                share_server.share_network_name),
            1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/shares/%s/\">%s</a></dd>" % (
                shares[0].id, shares[0].name),
            1, 200)
        self.assertContains(
            res,
            "<dd><a href=\"/admin/shares/%s/\">%s</a></dd>" % (
                shares[1].id, shares[1].id),
            1, 200)
        for k, v in share_server.backend_details.items():
            self.assertContains(res, "<dt>%s</dt>" % k)
            self.assertContains(res, "<dd>%s</dd>" % v)
        self.assertNoMessages()
        api_manila.share_server_get.assert_called_once_with(
            mock.ANY, share_server.id)
        api_manila.share_list.assert_called_once_with(
            mock.ANY, search_opts={"share_server_id": share_server.id})

    def test_detail_view_share_server_with_exception(self):
        share_server = test_data.share_server
        url = reverse('horizon:admin:share_servers:share_server_detail',
                      args=[share_server.id])
        self.mock_object(
            api_manila, "share_server_get",
            mock.Mock(side_effect=horizon_exceptions.NotFound(404)))

        res = self.client.get(url)

        self.assertRedirectsNoFollow(res, INDEX_URL)
        api_manila.share_server_get.assert_called_once_with(
            mock.ANY, share_server.id)
