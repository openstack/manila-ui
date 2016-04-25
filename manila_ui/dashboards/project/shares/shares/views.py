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
Views for managing shares.
"""

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.project.shares.shares import forms \
    as share_form
from manila_ui.dashboards.project.shares.shares \
    import tables as shares_tables
from manila_ui.dashboards.project.shares.shares \
    import tabs as shares_tabs
from openstack_dashboard.usage import quotas


class ShareTableMixIn(object):
    def _get_shares(self, search_opts=None):
        try:
            return manila.share_list(self.request, search_opts=search_opts)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve share list.'))
            return []

    def _set_id_if_nameless(self, shares):
        for share in shares:
            # It is possible to create a share with no name
            if not share.name:
                share.name = share.id


class DetailView(tabs.TabView):
    tab_group_class = shares_tabs.ShareDetailTabs
    template_name = 'project/shares/shares/detail.html'

    def _calculate_size_of_longest_export_location(self, export_locations):
        size = 40
        for export_location in export_locations:
            current_size = len(export_location["path"])
            if current_size > size:
                size = current_size
        return size

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        share = self.get_data()
        share_display_name = share.name or share.id
        context["share"] = share
        context["share_display_name"] = share_display_name
        context["page_title"] = _("Share Details: "
                                  "%(share_display_name)s") % \
            {'share_display_name': share_display_name}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_id = self.kwargs['share_id']
            share = manila.share_get(self.request, share_id)
            share.rules = manila.share_rules_list(self.request, share_id)
            share.export_locations = manila.share_export_location_list(
                self.request, share_id)
            share.el_size = self._calculate_size_of_longest_export_location(
                share.export_locations)
        except Exception:
            redirect = reverse('horizon:project:shares:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve share details.'),
                              redirect=redirect)
        return share

    def get_tabs(self, request, *args, **kwargs):
        share = self.get_data()
        return self.tab_group_class(request, share=share, **kwargs)


class CreateView(forms.ModalFormView):
    form_class = share_form.CreateForm
    template_name = 'project/shares/shares/create.html'
    success_url = reverse_lazy("horizon:project:shares:index")
    page_title = _('Create a Share')

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        try:
            context['usages'] = quotas.tenant_limit_usages(self.request)
        except Exception:
            exceptions.handle(self.request)
        return context


class UpdateView(forms.ModalFormView):
    form_class = share_form.UpdateForm
    template_name = 'project/shares/shares/update.html'
    success_url = reverse_lazy("horizon:project:shares:index")
    page_title = _('Edit Share')

    def get_object(self):
        if not hasattr(self, "_object"):
            vol_id = self.kwargs['share_id']
            try:
                self._object = manila.share_get(self.request, vol_id)
            except Exception:
                msg = _('Unable to retrieve share.')
                url = reverse('horizon:project:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['share'] = self.get_object()
        return context

    def get_initial(self):
        share = self.get_object()
        return {'share_id': self.kwargs["share_id"],
                'name': share.name,
                'description': share.description}


class UpdateMetadataView(forms.ModalFormView):
    form_class = share_form.UpdateMetadataForm
    template_name = 'project/shares/shares/update_metadata.html'
    success_url = reverse_lazy("horizon:project:shares:index")
    page_title = _('Edit Share Metadata')

    def get_object(self):
        if not hasattr(self, "_object"):
            vol_id = self.kwargs['share_id']
            try:
                self._object = manila.share_get(self.request, vol_id)
            except Exception:
                msg = _('Unable to retrieve share.')
                url = reverse('horizon:project:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateMetadataView, self).get_context_data(**kwargs)
        context['share'] = self.get_object()
        return context

    def get_initial(self):
        share = self.get_object()
        return {'share_id': self.kwargs["share_id"],
                'metadata': share.metadata}


class AddRuleView(forms.ModalFormView):
    form_class = share_form.AddRule
    template_name = 'project/shares/shares/rule_add.html'
    page_title = _('Add Rule')

    def get_object(self):
        if not hasattr(self, "_object"):
            vol_id = self.kwargs['share_id']
            try:
                self._object = manila.share_get(self.request, vol_id)
            except Exception:
                msg = _('Unable to retrieve share.')
                url = reverse('horizon:project:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(AddRuleView, self).get_context_data(**kwargs)
        context['share'] = self.get_object()
        return context

    def get_initial(self):
        share = self.get_object()
        return {'share_id': self.kwargs["share_id"],
                'name': share.name,
                'description': share.description}

    def get_success_url(self):
        return reverse("horizon:project:shares:manage_rules",
                       args=[self.kwargs['share_id']])


class ManageRulesView(tables.DataTableView):
    table_class = shares_tables.RulesTable
    template_name = 'project/shares/shares/manage_rules.html'

    def get_context_data(self, **kwargs):
        context = super(ManageRulesView, self).get_context_data(**kwargs)
        share = manila.share_get(self.request, self.kwargs['share_id'])
        context['share_display_name'] = share.name or share.id
        context["share"] = self.get_data()
        context["page_title"] = _("Share Rules: "
                                  "%(share_display_name)s") % \
            {'share_display_name': context['share_display_name']}
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_id = self.kwargs['share_id']
            rules = manila.share_rules_list(self.request, share_id)
        except Exception:
            redirect = reverse('horizon:project:shares:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve share rules.'),
                              redirect=redirect)
        return rules


class ExtendView(forms.ModalFormView):
    form_class = share_form.ExtendForm
    template_name = 'project/shares/shares/extend.html'
    success_url = reverse_lazy("horizon:project:shares:index")
    page_title = _('Extend Share')

    def get_object(self):
        if not hasattr(self, "_object"):
            share_id = self.kwargs['share_id']
            try:
                self._object = manila.share_get(self.request, share_id)
            except Exception:
                msg = _('Unable to retrieve share.')
                url = reverse('horizon:project:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(ExtendView, self).get_context_data(**kwargs)
        context['share'] = self.get_object()

        try:
            context['usages'] = quotas.tenant_limit_usages(self.request)
        except Exception:
            exceptions.handle(self.request)

        return context

    def get_initial(self):
        share = self.get_object()
        return {'share_id': self.kwargs["share_id"],
                'name': share.name,
                'orig_size': share.size,
                'new_size': int(share.size) + 1
                }
