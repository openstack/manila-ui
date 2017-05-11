# Copyright 2017 Mirantis, Inc.
# All rights reserved.
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

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import workflows
from openstack_dashboard.api import keystone

from manila_ui.api import manila


class AddProjectAction(workflows.MembershipAction):

    def __init__(self, request, *args, **kwargs):
        super(AddProjectAction, self).__init__(request, *args, **kwargs)
        default_role_field_name = self.get_default_role_field_name()
        self.fields[default_role_field_name] = forms.CharField(required=False)
        self.fields[default_role_field_name].initial = 'member'

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)
        share_group_type_id = self.initial['id']

        # Get list of existing projects
        try:
            projects, __ = keystone.tenant_list(request)
        except Exception:
            err_msg = _('Unable to get list of projects.')
            exceptions.handle(request, err_msg)

        # Get list of projects with access to this Share Group Type
        try:
            share_group_type = manila.share_group_type_get(
                request, share_group_type_id)
            self.share_group_type_name = share_group_type.name
            projects_initial = manila.share_group_type_access_list(
                request, share_group_type)
        except Exception:
            err_msg = _(
                'Unable to get information about share group type access.')
            exceptions.handle(request, err_msg)

        self.fields[field_name].choices = [
            (project.id, project.name or project.id) for project in projects]
        self.fields[field_name].initial = [
            pr.project_id for pr in projects_initial]
        self.projects_initial = set(self.fields[field_name].initial)

    class Meta(object):
        name = _("Projects with access to share group type")
        slug = "update_members"

    def handle(self, request, context):
        context.update({
            'name': self.share_group_type_name,
            'projects_add': self.projects_allow - self.projects_initial,
            'projects_remove': self.projects_initial - self.projects_allow,
        })
        return context

    def clean(self):
        cleaned_data = super(AddProjectAction, self).clean()
        self.projects_allow = set(
            cleaned_data[self.get_member_field_name('member')])
        return cleaned_data


class AddProjectStep(workflows.UpdateMembersStep):
    action_class = AddProjectAction
    available_list_title = _("Available projects")
    help_text = _("Allow project access to share group type.")
    members_list_title = _("Selected projects")
    no_available_text = _("No projects found.")
    no_members_text = _("No projects selected.")
    depends_on = ("id", )
    show_roles = False


class ManageShareGroupTypeAccessWorkflow(workflows.Workflow):
    slug = "manage_share_group_type_access"
    name = _("Manage Share Group Type Access")
    finalize_button_name = _("Manage Share Group Type Access")
    success_message = _('Updated access for share group type "%s".')
    failure_message = _('Unable to update access for share group type "%s".')
    success_url = 'horizon:admin:share_group_types:index'
    default_steps = (AddProjectStep, )

    def format_status_message(self, message):
        return message % self.context['name']

    def handle(self, request, context):
        try:
            for project in self.context['projects_remove']:
                manila.share_group_type_access_remove(
                    request, self.context['id'], project)
            for project in self.context['projects_add']:
                manila.share_group_type_access_add(
                    request, self.context['id'], project)
            return True
        except Exception:
            exceptions.handle(request, _('Unable to update share group type.'))
            return False
