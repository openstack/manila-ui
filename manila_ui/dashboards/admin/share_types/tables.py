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

from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from horizon import tables

from manila_ui.api import manila


def get_size(share):
    return _("%sGiB") % share.size


class CreateShareType(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Share Type")
    url = "horizon:admin:share_types:create_type"
    classes = ("ajax-modal", "btn-create")
    icon = "plus"


class DeleteShareType(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            "Delete Share Type",
            "Delete Share Types",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            "Deleted Share Type",
            "Deleted Share Types",
            count
        )

    def delete(self, request, obj_id):
        manila.share_type_delete(request, obj_id)


class ManageShareTypeAccess(tables.LinkAction):
    name = "manage"
    verbose_name = _("Manage Share Type Access")
    url = "horizon:admin:share_types:manage_share_type_access"
    classes = ("ajax-modal", "btn-create")

    def allowed(self, request, obj_id):
        st = manila.share_type_get(request, obj_id)
        # Enable it only for private share types
        return not st.is_public

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}


class UpdateShareType(tables.LinkAction):
    name = "update share type"
    verbose_name = _("Update Share Type")
    url = "horizon:admin:share_types:update_type"
    classes = ("ajax-modal", "btn-create")

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}


class ShareTypesFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = (
        ('name', _("Name") + " ", True),
        ('extra_specs', _("Extra Spec") + " ", True),
    )


class ShareTypesTable(tables.DataTable):
    name = tables.WrappingColumn("name", verbose_name=_("Name"))
    description = tables.WrappingColumn(
        "description", verbose_name=_("Description"))
    extra_specs = tables.Column("extra_specs", verbose_name=_("Extra specs"), )
    is_default = tables.Column(
        "is_default", verbose_name=_("Is default"),
        filters=(lambda d: 'Yes' if d is True else '-', ),
    )
    visibility = tables.Column(
        "is_public", verbose_name=_("Visibility"),
        filters=(lambda d: 'public' if d is True else 'private', ),
    )

    def get_object_display(self, share_type):
        return share_type.name

    def get_object_id(self, share_type):
        return str(share_type.id)

    class Meta(object):
        name = "share_types"
        verbose_name = _("Share Types")
        table_actions = (
            ShareTypesFilterAction,
            CreateShareType,
            DeleteShareType,
        )
        row_actions = (
            UpdateShareType,
            ManageShareTypeAccess,
            DeleteShareType,
        )
