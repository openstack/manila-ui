# Copyright (c) 2014 NetApp, Inc.
# All rights reserved.

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


class Create(tables.LinkAction):
    name = "create_security_service"
    verbose_name = _("Create Security Service")
    url = "horizon:project:security_services:security_service_create"
    classes = ("ajax-modal", "btn-create")
    icon = "plus"
    policy_rules = (("share", "security_service:create"),)


class Delete(tables.DeleteAction):
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


class Edit(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Security Service")
    url = "horizon:project:security_services:security_service_update"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "security_service:update"),)


class SecurityServicesTable(tables.DataTable):
    name = tables.WrappingColumn(
        "name", verbose_name=_("Name"),
        link="horizon:project:security_services:security_service_detail")
    dns_ip = tables.Column("dns_ip", verbose_name=_("DNS IP"))
    server = tables.Column("server", verbose_name=_("Server"))
    domain = tables.Column("domain", verbose_name=_("Domain"))
    user = tables.Column("user", verbose_name=_("User"))

    def get_object_display(self, security_service):
        return security_service.name or str(security_service.id)

    def get_object_id(self, security_service):
        return str(security_service.id)

    class Meta(object):
        name = "security_services"
        verbose_name = _("Security Services")
        table_actions = (
            tables.NameFilterAction,
            Create,
            Delete)
        row_actions = (
            Edit,
            Delete)
