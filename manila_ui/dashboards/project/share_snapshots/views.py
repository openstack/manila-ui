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

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.project.share_snapshots import forms as ss_forms
from manila_ui.dashboards.project.share_snapshots import tables as ss_tables
from manila_ui.dashboards.project.share_snapshots import tabs as ss_tabs
from manila_ui.dashboards import utils as ui_utils


class ShareSnapshotsView(tables.MultiTableView):
    table_classes = (
        ss_tables.ShareSnapshotsTable,
    )
    template_name = "project/share_snapshots/index.html"
    page_title = _("Share Snapshots")

    @memoized.memoized_method
    def get_share_snapshots_data(self):
        try:
            snapshots = manila.share_snapshot_list(self.request)
            shares = manila.share_list(self.request)
            share_names = dict([(share.id, share.name or share.id)
                                for share in shares])
            for snapshot in snapshots:
                snapshot.share = share_names.get(snapshot.share_id)
        except Exception:
            msg = _("Unable to retrieve share snapshots list.")
            exceptions.handle(self.request, msg)
            return []
        # Gather our tenants to correlate against IDs
        return snapshots


class ShareSnapshotDetailView(tabs.TabView):
    tab_group_class = ss_tabs.ShareSnapshotDetailTabs
    template_name = 'project/share_snapshots/detail.html'
    redirect_url = reverse_lazy('horizon:project:share_snapshots:index')

    def get_context_data(self, **kwargs):
        context = super(ShareSnapshotDetailView, self).get_context_data(
            **kwargs)
        snapshot = self.get_data()
        snapshot_display_name = snapshot.name or snapshot.id
        context["snapshot"] = snapshot
        context["snapshot_display_name"] = snapshot_display_name
        context["page_title"] = _("Snapshot Details: "
                                  "%(snapshot_display_name)s") % (
            {'snapshot_display_name': snapshot_display_name})
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            snapshot_id = self.kwargs['snapshot_id']
            snapshot = manila.share_snapshot_get(self.request, snapshot_id)
            share = manila.share_get(self.request, snapshot.share_id)
            if share.mount_snapshot_support:
                snapshot.rules = manila.share_snapshot_rules_list(
                    self.request, snapshot_id)
                snapshot.export_locations = (
                    manila.share_snap_export_location_list(
                        self.request, snapshot))
                export_locations = [
                    exp['path'] for exp in snapshot.export_locations
                ]
                snapshot.el_size = ui_utils.calculate_longest_str_size(
                    export_locations)

            snapshot.share_name_or_id = share.name or share.id
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve snapshot details.'),
                redirect=self.redirect_url)
        return snapshot

    def get_tabs(self, request, *args, **kwargs):
        snapshot = self.get_data()
        return self.tab_group_class(request, snapshot=snapshot, **kwargs)


class CreateShareSnapshotView(forms.ModalFormView):
    form_class = ss_forms.CreateShareSnapshotForm
    form_id = "create_share_snapshot"
    template_name = 'project/share_snapshots/create.html'
    modal_header = _("Create Share Snapshot")
    modal_id = "create_share_snapshot_modal"
    submit_label = _("Create Share Snapshot")
    submit_url = "horizon:project:share_snapshots:share_snapshot_create"
    success_url = reverse_lazy('horizon:project:share_snapshots:index')
    page_title = _('Create Share Snapshot')

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['share_id'] = self.kwargs['share_id']
        try:
            context['usages'] = manila.tenant_absolute_limits(self.request)
        except Exception:
            exceptions.handle(self.request, _('Unable to retrieve quotas.'))
        return context

    def get_initial(self):
        self.submit_url = reverse(self.submit_url, kwargs=self.kwargs)
        return {'share_id': self.kwargs["share_id"]}


class UpdateShareSnapshotView(forms.ModalFormView):
    form_class = ss_forms.UpdateShareSnapshotForm
    form_id = "update_share_snapshot"
    template_name = 'project/share_snapshots/update.html'
    modal_header = _("Update Share Snapshot")
    modal_id = "update_share_snapshot_modal"
    submit_label = _("Update")
    submit_url = "horizon:project:share_snapshots:share_snapshot_edit"
    success_url = reverse_lazy('horizon:project:share_snapshots:index')
    page_title = _('Edit Share Snapshot')

    @memoized.memoized_method
    def get_object(self):
        if not hasattr(self, "_object"):
            snap_id = self.kwargs['snapshot_id']
            try:
                self._object = manila.share_snapshot_get(self.request, snap_id)
            except Exception:
                msg = _('Unable to retrieve share snapshot.')
                url = reverse('horizon:project:share_snapshots:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        args = (self.get_object().id,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        snapshot = self.get_object()
        return {'snapshot_id': self.kwargs["snapshot_id"],
                'name': snapshot.name,
                'description': snapshot.description}


class AddShareSnapshotRuleView(forms.ModalFormView):
    form_class = ss_forms.AddShareSnapshotRule
    form_id = "rule_add_snap"
    template_name = 'project/share_snapshots/rule_add.html'
    modal_header = _("Add Rule")
    modal_id = "rule_add_share_snapshot_modal"
    submit_label = _("Add")
    submit_url = "horizon:project:share_snapshots:share_snapshot_rule_add"
    success_url = reverse_lazy("horizon:project:share_snapshots:index")
    page_title = _('Add Rule')

    def get_object(self):
        if not hasattr(self, "_object"):
            snapshot_id = self.kwargs['snapshot_id']
            try:
                self._object = manila.share_snapshot_get(
                    self.request, snapshot_id)
            except Exception:
                msg = _('Unable to retrieve snapshot.')
                url = reverse('horizon:project:share_snapshots:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        args = (self.get_object().id,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        snapshot = self.get_object()
        return {'snapshot_id': self.kwargs["snapshot_id"],
                'name': snapshot.name,
                'description': snapshot.description}

    def get_success_url(self):
        return reverse(
            "horizon:project:share_snapshots:share_snapshot_manage_rules",
            args=[self.kwargs['snapshot_id']])


class ManageShareSnapshotRulesView(tables.DataTableView):
    table_class = ss_tables.ShareSnapshotRulesTable
    template_name = 'project/share_snapshots/manage_rules.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        snapshot = manila.share_snapshot_get(
            self.request, self.kwargs['snapshot_id'])
        context['snapshot_display_name'] = snapshot.name or snapshot.id
        context["snapshot"] = self.get_data()
        context["page_title"] = _("Snapshot Rules: "
                                  "%(snapshot_display_name)s") % {
            'snapshot_display_name': context['snapshot_display_name']}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            snapshot_id = self.kwargs['snapshot_id']
            rules = manila.share_snapshot_rules_list(
                self.request, snapshot_id)
        except Exception:
            redirect = reverse('horizon:project:share_snapshots:index')
            exceptions.handle(
                self.request,
                _('Unable to retrieve share snapshot rules.'),
                redirect=redirect)
        return rules
