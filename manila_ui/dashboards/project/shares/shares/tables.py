# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
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

from django.core.urlresolvers import NoReverseMatch  # noqa
from django.core.urlresolvers import reverse
from django.template.defaultfilters import title  # noqa
from django.utils.safestring import mark_safe
from django.utils.translation import string_concat, ugettext_lazy  # noqa
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import messages
from horizon import tables
from manila_ui.api import manila
from manila_ui.dashboards.project.shares.snapshots \
    import tables as snapshot_tables
from manila_ui.dashboards import utils
from openstack_dashboard.usage import quotas


DELETABLE_STATES = (
    "AVAILABLE", "ERROR",
    "MANAGE_ERROR",
)


class DeleteShare(tables.DeleteAction):
    data_type_singular = _("Share")
    data_type_plural = _("Shares")
    action_past = _("Scheduled deletion of %(data_type)s")
    policy_rules = (("share", "share:delete"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}

    def delete(self, request, obj_id):
        try:
            manila.share_delete(request, obj_id)
        except Exception:
            msg = _('Unable to delete share "%s". ') % obj_id
            messages.error(request, msg)

    def allowed(self, request, share=None):
        if share:
            # Row button
            return (share.status.upper() in DELETABLE_STATES and
                    not getattr(share, 'has_snapshot', False))
        # Table button. Always return 'True'.
        return True


class CreateShare(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Share")
    url = "horizon:project:shares:create"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share:create"),)

    def allowed(self, request, share=None):
        usages = quotas.tenant_quota_usages(request)
        if usages['shares']['available'] <= 0:
            if "disabled" not in self.classes:
                self.classes = [c for c in self.classes] + ['disabled']
                self.verbose_name = string_concat(self.verbose_name, ' ',
                                                  _("(Quota exceeded)"))
        else:
            self.verbose_name = _("Create Share")
            classes = [c for c in self.classes if c != "disabled"]
            self.classes = classes
        return True


class EditShare(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Share")
    url = "horizon:project:shares:update"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share:update"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}

    def allowed(self, request, share=None):
        return share.status in ("available", "in-use")


class EditShareMetadata(tables.LinkAction):
    name = "update_metadata"
    verbose_name = _("Edit Share Metadata")
    url = "horizon:project:shares:update_metadata"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share:update_share_metadata"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}

    def allowed(self, request, share=None):
        return share.status in ("available", "in-use")


class ExtendShare(tables.LinkAction):
    name = "extend_share"
    verbose_name = _("Extend Share")
    url = "horizon:project:shares:extend"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share:extend"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}

    def allowed(self, request, share=None):
        return share.status.lower() in ("available",)


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, share_id):
        share = manila.share_get(request, share_id)
        if not share.name:
            share.name = share_id
        if share.share_network_id:
            share_net = manila.share_network_get(request,
                                                 share.share_network_id)
            share.share_network = share_net.name or share_net.id
        else:
            share.share_network = None
        meta_str = utils.metadata_to_str(share.metadata)
        share.metadata = mark_safe(meta_str)

        return share


def get_size(share):
    return _("%sGiB") % share.size


class SharesTableBase(tables.DataTable):
    STATUS_CHOICES = (
        ("available", True), ("AVAILABLE", True),
        ("creating", None), ("CREATING", None),
        ("deleting", None), ("DELETING", None),
        ("error", False), ("ERROR", False),
        ("error_deleting", False), ("ERROR_DELETING", False),
        ("MANAGE_ERROR", False),
        ("UNMANAGE_ERROR", False),
        ("extending_error", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("available", pgettext_lazy("Current status of share", u"Available")),
        ("AVAILABLE", pgettext_lazy("Current status of share", u"Available")),
        ("creating", pgettext_lazy("Current status of share", u"Creating")),
        ("CREATING", pgettext_lazy("Current status of share", u"Creating")),
        ("deleting", pgettext_lazy("Current status of share", u"Deleting")),
        ("DELETING", pgettext_lazy("Current status of share", u"Deleting")),
        ("error", pgettext_lazy("Current status of share", u"Error")),
        ("ERROR", pgettext_lazy("Current status of share", u"Error")),
        ("error_deleting", pgettext_lazy("Current status of share",
                                         u"Deleting")),
        ("ERROR_DELETING", pgettext_lazy("Current status of share",
                                         u"Deleting")),
        ("MANAGE_ERROR", pgettext_lazy("Current status of share",
                                       u"Manage Error")),
        ("UNMANAGE_ERROR", pgettext_lazy("Current status of share",
                                         u"Unmanage Error")),
        ("extending_error", pgettext_lazy("Current status of share",
                                          u"Extending Error")),
    )
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:project:shares:detail")
    description = tables.Column("description",
                                verbose_name=_("Description"),
                                truncate=40)
    metadata = tables.Column("metadata",
                             verbose_name=_("Metadata"))
    size = tables.Column(get_size,
                         verbose_name=_("Size"),
                         attrs={'data-type': 'size'})
    status = tables.Column("status",
                           filters=(title,),
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES,
                           display_choices=STATUS_DISPLAY_CHOICES)

    def get_object_display(self, obj):
        return obj.name or obj.id


class SharesFilterAction(tables.FilterAction):

    def filter(self, table, shares, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [share for share in shares
                if q in share.name.lower()]


class ManageRules(tables.LinkAction):
    name = "manage_rules"
    verbose_name = _("Manage Rules")
    url = "horizon:project:shares:manage_rules"
    classes = ("btn-edit", )
    policy_rules = (("share", "share:access_get_all"),)


class AddRule(tables.LinkAction):
    name = "rule_add"
    verbose_name = _("Add rule")
    url = 'horizon:project:shares:rule_add'
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share:allow_access"),)

    def allowed(self, request, share=None):
        share = manila.share_get(request, self.table.kwargs['share_id'])
        return share.status in ("available", "in-use")

    def get_link_url(self):
        return reverse(self.url, args=[self.table.kwargs['share_id']])


class DeleteRule(tables.DeleteAction):
    data_type_singular = _("Rule")
    data_type_plural = _("Rules")
    action_past = _("Scheduled deletion of %(data_type)s")
    policy_rules = (("share", "share:deny_access"),)

    def delete(self, request, obj_id):
        try:
            manila.share_deny(request, self.table.kwargs['share_id'], obj_id)
        except Exception:
            msg = _('Unable to delete rule "%s".') % obj_id
            exceptions.handle(request, msg)


class UpdateRuleRow(tables.Row):
    ajax = True

    def get_data(self, request, rule_id):
        rules = manila.share_rules_list(request, self.table.kwargs['share_id'])
        if rules:
            for rule in rules:
                if rule.id == rule_id:
                    return rule
        raise exceptions.NotFound


class RulesTable(tables.DataTable):
    access_type = tables.Column("access_type", verbose_name=_("Access Type"))
    access_to = tables.Column("access_to", verbose_name=_("Access to"))
    access_level = tables.Column(
        "access_level", verbose_name=_("Access Level"))
    status = tables.Column("state", verbose_name=_("Status"))

    def get_object_display(self, obj):
        return obj.id

    class Meta(object):
        name = "rules"
        verbose_name = _("Rules")
        status_columns = ["status"]
        row_class = UpdateRuleRow
        table_actions = (DeleteRule, AddRule)
        row_actions = (DeleteRule, )


def get_share_network(share):
    name = share.share_network_name
    return name if name != "None" else None


class SharesTable(SharesTableBase):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:project:shares:detail")
    visibility = tables.Column(
        "is_public", verbose_name=_("Visibility"),
        help_text=("Whether this share visible to all tenants (public) or "
                   "only for owner (private)."),
        filters=(lambda d: 'public' if d is True else 'private', ),
    )
    proto = tables.Column("share_proto", verbose_name=_("Protocol"))
    share_network = tables.Column("share_network",
                                  verbose_name=_("Share Network"),
                                  empty_value="-")

    class Meta(object):
        name = "shares"
        verbose_name = _("Shares")
        status_columns = ["status"]
        row_class = UpdateRow
        table_actions = (CreateShare, DeleteShare, SharesFilterAction)
        row_actions = (EditShare, ExtendShare, snapshot_tables.CreateSnapshot,
                       DeleteShare, ManageRules, EditShareMetadata)
