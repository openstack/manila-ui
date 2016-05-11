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

"""
Admin views for managing shares.
"""

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon.utils import memoized
from horizon import workflows

from manila_ui.api import manila
from manila_ui.dashboards.admin.shares import forms as project_forms
from manila_ui.dashboards.admin.shares import tabs as project_tabs
import manila_ui.dashboards.admin.shares.workflows as share_workflows
from manila_ui.dashboards.project.shares.security_services import \
    views as ss_views
from manila_ui.dashboards.project.shares.share_networks import \
    views as sn_views
from manila_ui.dashboards.project.shares.shares import views as share_views
from manila_ui.dashboards.project.shares.snapshots import \
    views as snapshot_views
from manila_ui.utils import filters

filters = (filters.get_item,)


class IndexView(tabs.TabbedTableView, share_views.ShareTableMixIn):
    tab_group_class = project_tabs.ShareTabs
    template_name = "admin/shares/index.html"
    page_title = _("Shares")


class DetailView(share_views.DetailView):
    template_name = "admin/shares/detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["page_title"] = _("Share Details: %(share_name)s") % \
            {'share_name': context["share_display_name"]}
        return context


class SecurityServiceDetailView(ss_views.Detail):
    redirect_url = reverse_lazy('horizon:admin:shares:index')


class ShareNetworkDetailView(sn_views.Detail):
    redirect_url = reverse_lazy('horizon:admin:shares:index')


class SnapshotDetailView(snapshot_views.SnapshotDetailView):
    redirect_url = reverse_lazy('horizon:admin:shares:index')


class ManageShareView(forms.ModalFormView):
    form_class = project_forms.ManageShare
    template_name = 'admin/shares/manage_share.html'
    modal_header = _("Manage Share")
    form_id = "manage_share_modal"
    submit_label = _("Manage")
    success_url = reverse_lazy('horizon:admin:shares:index')
    submit_url = reverse_lazy('horizon:admin:shares:manage')
    cancel_url = reverse_lazy('horizon:admin:shares:index')
    page_title = _("Manage a Share")

    def get_context_data(self, **kwargs):
        context = super(ManageShareView, self).get_context_data(**kwargs)
        return context


class UnmanageShareView(forms.ModalFormView):
    form_class = project_forms.UnmanageShare
    template_name = 'admin/shares/unmanage_share.html'
    modal_header = _("Confirm Unmanage Share")
    form_id = "unmanage_share_modal"
    submit_label = _("Unmanage")
    success_url = reverse_lazy('horizon:admin:shares:index')
    submit_url = 'horizon:admin:shares:unmanage'
    cancel_url = reverse_lazy('horizon:admin:shares:index')
    page_title = _("Unmanage a Share")

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


class CreateShareTypeView(forms.ModalFormView):
    form_class = project_forms.CreateShareType
    template_name = 'admin/shares/create_share_type.html'
    success_url = 'horizon:admin:shares:index'
    page_title = _("Create a Share Type")

    def get_success_url(self):
        return reverse(self.success_url)


class ManageShareTypeAccessView(workflows.WorkflowView):
    workflow_class = share_workflows.ManageShareTypeAccessWorkflow
    template_name = "admin/shares/manage_share_type_access.html"
    success_url = 'horizon:project:shares:index'
    page_title = _("Manage Share Type Access")

    def get_initial(self):
        return {'id': self.kwargs["share_type_id"]}

    def get_context_data(self, **kwargs):
        context = super(ManageShareTypeAccessView, self).get_context_data(
            **kwargs)
        context['id'] = self.kwargs['share_type_id']
        return context


class UpdateShareTypeView(forms.ModalFormView):
    form_class = project_forms.UpdateShareType
    template_name = "admin/shares/update_share_type.html"
    success_url = reverse_lazy("horizon:admin:shares:index")
    page_title = _("Update Share Type")

    def get_object(self):
        if not hasattr(self, "_object"):
            st_id = self.kwargs["share_type_id"]
            try:
                self._object = manila.share_type_get(self.request, st_id)
            except Exception:
                msg = _("Unable to retrieve share_type.")
                url = reverse("horizon:admin:shares:index")
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateShareTypeView, self).get_context_data(**kwargs)
        context["share_type"] = self.get_object()
        return context

    def get_initial(self):
        share_type = self.get_object()
        return {
            "id": self.kwargs["share_type_id"],
            "name": share_type.name,
            "extra_specs": share_type.extra_specs,
        }


class ShareServDetail(tabs.TabView):
    tab_group_class = project_tabs.ShareServerDetailTabs
    template_name = 'admin/shares/detail_share_server.html'

    def get_context_data(self, **kwargs):
        context = super(ShareServDetail, self).get_context_data(**kwargs)
        share_server = self.get_data()
        share_server_display_name = share_server.id
        context["share_server"] = share_server
        context["share_server_display_name"] = share_server_display_name
        context["page_title"] = _("Share Server Details: %(server_name)s") % \
            {'server_name': share_server_display_name}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_serv_id = self.kwargs['share_server_id']
            share_serv = manila.share_server_get(self.request, share_serv_id)
            share_search_opts = {'share_server_id': share_serv.id}
            shares_list = manila.share_list(self.request,
                                            search_opts=share_search_opts)
            for share in shares_list:
                share.name_or_id = share.name or share.id
            share_serv.shares_list = shares_list
            if not hasattr(share_serv, 'share_network_id'):
                share_serv.share_network_id = None

        except Exception:
            redirect = reverse('horizon:admin:shares:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve share server details.'),
                              redirect=redirect)
        return share_serv

    def get_tabs(self, request, *args, **kwargs):
        share_server = self.get_data()
        return self.tab_group_class(request, share_server=share_server,
                                    **kwargs)


class ShareInstanceDetailView(tabs.TabView):
    tab_group_class = project_tabs.ShareInstanceDetailTabs
    template_name = 'admin/shares/share_instance_detail.html'

    def _calculate_size_of_longest_export_location(self, export_locations):
        size = 40
        for export_location in export_locations:
            if len(export_location["path"]) > size:
                size = len(export_location["path"])
        return size

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        share_instance = self.get_data()
        context["share_instance"] = share_instance
        context["page_title"] = (
            _("Share Instance Details: %s") % share_instance.id)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_instance_id = self.kwargs['share_instance_id']
            share_instance = manila.share_instance_get(
                self.request, share_instance_id)
            share_instance.export_locations = (
                manila.share_instance_export_location_list(
                    self.request, share_instance_id))
            share_instance.el_size = (
                self._calculate_size_of_longest_export_location(
                    share_instance.export_locations))
            return share_instance
        except Exception:
            redirect = reverse('horizon:admin:shares:index')
            exceptions.handle(
                self.request,
                _('Unable to retrieve share instance details.'),
                redirect=redirect)

    def get_tabs(self, request, *args, **kwargs):
        share_instance = self.get_data()
        return self.tab_group_class(
            request, share_instance=share_instance, **kwargs)
