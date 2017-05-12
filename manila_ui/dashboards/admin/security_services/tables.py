# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables

from manila_ui.api import manila


class DeleteSecurityService(tables.DeleteAction):
    policy_rules = (("share", "security_service:delete"),)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Security Service",
            u"Delete Security Services",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Security Service",
            u"Deleted Security Services",
            count
        )

    def delete(self, request, obj_id):
        manila.security_service_delete(request, obj_id)


class SecurityServicesTable(tables.DataTable):
    name = tables.WrappingColumn(
        "name", verbose_name=_("Name"),
        link="horizon:admin:security_services:security_service_detail")
    project = tables.Column("project_name", verbose_name=_("Project"))
    dns_ip = tables.Column("dns_ip", verbose_name=_("DNS IP"))
    server = tables.Column("server", verbose_name=_("Server"))
    domain = tables.Column("domain", verbose_name=_("Domain"))
    user = tables.Column("user", verbose_name=_("Sid"))

    def get_object_display(self, security_service):
        return security_service.name

    def get_object_id(self, security_service):
        return str(security_service.id)

    class Meta(object):
        name = "security_services"
        verbose_name = _("Security Services")
        table_actions = (
            tables.NameFilterAction,
            DeleteSecurityService,
        )
        row_actions = (
            DeleteSecurityService,
        )
