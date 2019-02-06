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


from openstack_dashboard.test.integration_tests import helpers


class TestManilaDashboardInstalled(helpers.TestCase):
    def test_shares_page_opened(self):
        shares_page = self.home_pg.go_to_project_share_sharespage()
        self.assertEqual(shares_page.page_title,
                         'Shares - OpenStack Dashboard')

    def test_share_snapshots_page_opened(self):
        s_snaps_page = self.home_pg.go_to_project_share_sharesnapshotspage()
        self.assertEqual(s_snaps_page.page_title,
                         'Share Snapshots - OpenStack Dashboard')

    def test_share_networks_page_opened(self):
        s_networks_page = self.home_pg.go_to_project_share_sharenetworkspage()
        self.assertEqual(s_networks_page.page_title,
                         'Share Networks - OpenStack Dashboard')

    def test_security_services_page_opened(self):
        sec_serv_page = self.home_pg.go_to_project_share_securityservicespage()
        self.assertEqual(sec_serv_page.page_title,
                         'Security Services - OpenStack Dashboard')

    def test_share_groups_page_opened(self):
        share_groups_page = self.home_pg.go_to_project_share_sharegroupspage()
        self.assertEqual(share_groups_page.page_title,
                         'Share Groups - OpenStack Dashboard')

    def test_share_group_snapthots_page_opened(self):
        sg_s_page = self.home_pg.go_to_project_share_sharegroupsnapshotspage()
        self.assertEqual(sg_s_page.page_title,
                         'Share Group Snapshots - OpenStack Dashboard')


class TestManilaAdminDashboardInstalled(helpers.AdminTestCase):
    def test_shares_page_opened(self):
        shares_page = self.home_pg.go_to_admin_share_sharespage()
        self.assertEqual(shares_page.page_title,
                         'Shares - OpenStack Dashboard')

    def test_share_snapshots_page_opened(self):
        s_snapshots_page = self.home_pg.go_to_admin_share_sharesnapshotspage()
        # TODO(e0ne): fix page title and test
        self.assertEqual(s_snapshots_page.page_title,
                         'Shares - OpenStack Dashboard')

    def test_share_snapshot_types_page_opened(self):
        share_types_page = (
            self.home_pg.go_to_admin_share_sharetypespage())
        self.assertEqual(share_types_page.page_title,
                         'Share Types - OpenStack Dashboard')

    def test_share_networks_page_opened(self):
        s_networks_page = self.home_pg.go_to_admin_share_sharenetworkspage()
        self.assertEqual(s_networks_page.page_title,
                         'Share Networks - OpenStack Dashboard')

    def test_security_services_page_opened(self):
        sec_serv_page = self.home_pg.go_to_admin_share_securityservicespage()
        self.assertEqual(sec_serv_page.page_title,
                         'Security Services - OpenStack Dashboard')

    def test_share_servers_page_opened(self):
        share_serv_page = self.home_pg.go_to_admin_share_shareserverspage()
        self.assertEqual(share_serv_page.page_title,
                         'Share Servers - OpenStack Dashboard')

    def test_share_instences_page_opened(self):
        sec_serv_page = self.home_pg.go_to_admin_share_shareinstancespage()
        self.assertEqual(sec_serv_page.page_title,
                         'Share Instances - OpenStack Dashboard')

    def test_share_groups_page_opened(self):
        share_groups_page = self.home_pg.go_to_admin_share_sharegroupspage()
        self.assertEqual(share_groups_page.page_title,
                         'Share Groups - OpenStack Dashboard')

    def test_share_group_snapthots_page_opened(self):
        sg_s_page = self.home_pg.go_to_admin_share_sharegroupsnapshotspage()
        self.assertEqual(sg_s_page.page_title,
                         'Share Group Snapshots - OpenStack Dashboard')

    def test_share_group_types_page_opened(self):
        sg_types_page = self.home_pg.go_to_admin_share_sharegrouptypespage()
        self.assertEqual(sg_types_page.page_title,
                         'Share Group Types - OpenStack Dashboard')
