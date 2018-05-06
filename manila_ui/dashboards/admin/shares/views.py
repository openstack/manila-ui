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

"""
Admin views for managing shares.
"""

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.admin.shares import forms as project_forms
from manila_ui.dashboards.admin.shares import tables as s_tables
from manila_ui.dashboards.admin.shares import tabs as s_tabs
from manila_ui.dashboards.admin import utils
from manila_ui.dashboards.project.shares import views as share_views


class SharesView(tables.MultiTableView, share_views.ShareTableMixIn):
    table_classes = (
        s_tables.SharesTable,
    )
    template_name = "admin/shares/index.html"
    page_title = _("Shares")

    @memoized.memoized_method
    def get_shares_data(self):
        shares = []
        try:
            shares = manila.share_list(
                self.request, search_opts={'all_tenants': True})
            snapshots = manila.share_snapshot_list(
                self.request, detailed=True, search_opts={'all_tenants': True})
            share_ids_with_snapshots = []
            for snapshot in snapshots:
                share_ids_with_snapshots.append(snapshot.to_dict()['share_id'])
            for share in shares:
                if share.to_dict()['id'] in share_ids_with_snapshots:
                    setattr(share, 'has_snapshot', True)
                else:
                    setattr(share, 'has_snapshot', False)
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve share list.'))

        # Gather our projects to correlate against IDs
        utils.set_project_name_to_objects(self.request, shares)

        return shares


class DetailView(share_views.DetailView):
    tab_group_class = s_tabs.ShareDetailTabs
    template_name = "admin/shares/detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["page_title"] = _("Share Details: %(share_name)s") % {
            'share_name': context["share_display_name"]}
        return context


class ManageShareView(forms.ModalFormView):
    form_class = project_forms.ManageShare
    form_id = "manage_share"
    template_name = 'admin/shares/manage_share.html'
    modal_header = _("Manage Share")
    modal_id = "manage_share_modal"
    submit_label = _("Manage")
    success_url = reverse_lazy('horizon:admin:shares:index')
    submit_url = reverse_lazy('horizon:admin:shares:manage')
    page_title = _("Manage Share")

    def get_context_data(self, **kwargs):
        context = super(ManageShareView, self).get_context_data(**kwargs)
        return context


class MigrationStartView(forms.ModalFormView):
    form_class = project_forms.MigrationStart
    template_name = 'admin/shares/migration_start.html'
    modal_header = _("Migrate Share")
    form_id = "migration_start_share"
    modal_id = "migration_start_share_modal"
    submit_label = _("Start migration")
    success_url = reverse_lazy('horizon:admin:shares:index')
    submit_url = 'horizon:admin:shares:migration_start'
    cancel_url = reverse_lazy('horizon:admin:shares:index')
    page_title = _("Migrate a Share")

    def get_context_data(self, **kwargs):
        context = super(MigrationStartView, self).get_context_data(**kwargs)
        args = (self.kwargs['share_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_id = self.kwargs['share_id']
            share = manila.share_get(self.request, share_id)
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve share details.'),
                redirect=self.success_url)
        return share

    def get_initial(self):
        share = self.get_data()
        return {
            'share_id': self.kwargs["share_id"],
            'name': share.name,
        }


class MigrationCompleteView(forms.ModalFormView):
    form_class = project_forms.MigrationComplete
    template_name = 'admin/shares/migration_complete.html'
    modal_header = _("Confirm Migration Completion of Share")
    form_id = "migration_complete_share"
    modal_id = "migration_complete_share_modal"
    submit_label = _("Complete Migration")
    success_url = reverse_lazy('horizon:admin:shares:index')
    submit_url = 'horizon:admin:shares:migration_complete'
    cancel_url = reverse_lazy('horizon:admin:shares:index')
    page_title = _("Complete migration of a Share")

    def get_context_data(self, **kwargs):
        context = super(MigrationCompleteView, self).get_context_data(**kwargs)
        args = (self.kwargs['share_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_id = self.kwargs['share_id']
            share = manila.share_get(self.request, share_id)
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve share details.'),
                redirect=self.success_url)
        return share

    def get_initial(self):
        share = self.get_data()
        return {
            'share_id': self.kwargs["share_id"],
            'name': share.name,
        }


class MigrationCancelView(forms.ModalFormView):
    form_class = project_forms.MigrationCancel
    template_name = 'admin/shares/migration_cancel.html'
    modal_header = _("Confirm Migration Cancelling of Share")
    form_id = "migration_cancel_share"
    modal_id = "migration_cancel_share_modal"
    submit_label = _("Cancel Migration")
    success_url = reverse_lazy('horizon:admin:shares:index')
    submit_url = 'horizon:admin:shares:migration_cancel'
    cancel_url = reverse_lazy('horizon:admin:shares:index')
    page_title = _("Cancel migration of a Share")

    def get_context_data(self, **kwargs):
        context = super(MigrationCancelView, self).get_context_data(**kwargs)
        args = (self.kwargs['share_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_id = self.kwargs['share_id']
            share = manila.share_get(self.request, share_id)
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve share details.'),
                redirect=self.success_url)
        return share

    def get_initial(self):
        share = self.get_data()
        return {
            'share_id': self.kwargs["share_id"],
            'name': share.name,
        }


class MigrationGetProgressView(forms.ModalFormView):
    form_class = project_forms.MigrationGetProgress
    template_name = 'admin/shares/migration_get_progress.html'
    modal_header = _("Confirm Obtaining migration progress of Share")
    form_id = "migration_get_progress_share"
    modal_id = "migration_get_progress_share_modal"
    submit_label = _("Obtain Progress")
    success_url = reverse_lazy('horizon:admin:shares:index')
    submit_url = 'horizon:admin:shares:migration_get_progress'
    cancel_url = reverse_lazy('horizon:admin:shares:index')
    page_title = _("Obtain migration progress of a Share")

    def get_context_data(self, **kwargs):
        context = super(MigrationGetProgressView,
                        self).get_context_data(**kwargs)
        args = (self.kwargs['share_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_id = self.kwargs['share_id']
            share = manila.share_get(self.request, share_id)
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve share details.'),
                redirect=self.success_url)
        return share

    def get_initial(self):
        share = self.get_data()
        return {
            'share_id': self.kwargs["share_id"],
            'name': share.name,
        }


class UnmanageShareView(forms.ModalFormView):
    form_class = project_forms.UnmanageShare
    form_id = "unmanage_share"
    template_name = 'admin/shares/unmanage_share.html'
    modal_header = _("Confirm Unmanage Share")
    modal_id = "unmanage_share_modal"
    submit_label = _("Unmanage")
    success_url = reverse_lazy('horizon:admin:shares:index')
    submit_url = 'horizon:admin:shares:unmanage'
    page_title = _("Unmanage Share")

    def get_context_data(self, **kwargs):
        context = super(UnmanageShareView, self).get_context_data(**kwargs)
        args = (self.kwargs['share_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_id = self.kwargs['share_id']
            share = manila.share_get(self.request, share_id)
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve volume details.'),
                redirect=self.success_url)
        return share

    def get_initial(self):
        share = self.get_data()
        return {
            'share_id': self.kwargs["share_id"],
            'name': share.name,
            'host': getattr(share, "host"),
        }
