# Copyright 2017 Mirantis, Inc.
# All rights reserved.
#
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
import six

from manila_ui.api import manila


class CreateShareGroupType(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Share Group Type")
    url = "horizon:admin:share_group_types:create"
    classes = ("ajax-modal", "btn-create")
    icon = "plus"


class DeleteShareGroupType(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Share Group Type",
            u"Delete Share Group Types",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Share Group Type",
            u"Deleted Share Group Types",
            count
        )

    def delete(self, request, obj_id):
        manila.share_group_type_delete(request, obj_id)


class ManageShareGroupTypeAccess(tables.LinkAction):
    name = "manage"
    verbose_name = _("Manage Share Group Type Access")
    url = "horizon:admin:share_group_types:manage_access"
    classes = ("ajax-modal", "btn-create")

    def allowed(self, request, obj_id):
        sgt = manila.share_group_type_get(request, obj_id)
        # Enable it only for private share group types
        return not sgt.is_public

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}


class UpdateShareGroupType(tables.LinkAction):
    name = "update share group type"
    verbose_name = _("Update Share group Type")
    url = "horizon:admin:share_group_types:update"
    classes = ("ajax-modal", "btn-create")

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}


class ShareGroupTypesTable(tables.DataTable):
    name = tables.WrappingColumn("name", verbose_name=_("Name"))
    group_specs = tables.Column("group_specs", verbose_name=_("Group specs"))
    share_types = tables.Column("share_types", verbose_name=_("Share types"))
    visibility = tables.Column(
        "is_public", verbose_name=_("Visibility"),
        filters=(lambda d: 'public' if d is True else 'private', ),
    )

    def get_object_display(self, share_group_type):
        return share_group_type.name

    def get_object_id(self, share_group_type):
        return six.text_type(share_group_type.id)

    class Meta(object):
        name = "share_group_types"
        verbose_name = _("Share Group Types")
        table_actions = (
            tables.NameFilterAction,
            CreateShareGroupType,
            DeleteShareGroupType,
        )
        row_actions = (
            UpdateShareGroupType,
            ManageShareGroupTypeAccess,
            DeleteShareGroupType,
        )
