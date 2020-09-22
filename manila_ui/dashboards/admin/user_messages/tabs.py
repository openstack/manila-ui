# Copyright (c) 2020 Red Hat, Inc.
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

from manila_ui.dashboards.project.user_messages import tabs as project_tabs


class UserMessagesOverviewTab(project_tabs.UserMessagesOverviewTab):
    template_name = "admin/user_messages/_detail.html"


class UserMessagesDetailTabs(project_tabs.UserMessagesDetailTabs):
    pass
