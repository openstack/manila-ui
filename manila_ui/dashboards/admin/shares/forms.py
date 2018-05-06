# Copyright (c) 2014 NetApp, Inc.
# All Rights Reserved.
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

from django.conf import settings
from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from oslo_utils import strutils
import six

from manila_ui.api import manila
from manila_ui.dashboards import utils


def _get_id_if_name_empty(data):
    result = data.get('name', None)
    if not result:
        result = data.get('id')
    if not result:
        result = ''
    return result


class MigrationStart(forms.SelfHandlingForm):
    name = forms.CharField(
        label=_("Share Name"),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    share_id = forms.CharField(
        label=_("ID"),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    host = forms.ChoiceField(
        label=_("Host to migrate share"),
        help_text=_("Destination host and pool where share will be migrated "
                    "to."))
    force_host_assisted_migration = forms.BooleanField(
        label=_("Force Host Assisted Migration"),
        required=False, initial=False,
        help_text=_("Enforces the use of the host-assisted migration approach,"
                    " which bypasses driver optimizations."))
    nondisruptive = forms.BooleanField(
        label=_("Nondisruptive"),
        required=False, initial=True,
        help_text=_("Enforces migration to be nondisruptive. If set to True, "
                    "host-assisted migration will not be attempted."))
    writable = forms.BooleanField(
        label=_("Writable"), required=False, initial=True,
        help_text=_("Enforces migration to keep the share writable while "
                    "contents are being moved. If set to True, host-assisted "
                    "migration will not be attempted."))
    preserve_metadata = forms.BooleanField(
        label=_("Preserve Metadata"), required=False, initial=True,
        help_text=_("Enforces migration to preserve all file metadata when "
                    "moving its contents. If set to True, host-assisted "
                    "migration will not be attempted."))
    preserve_snapshots = forms.BooleanField(
        label=_("Preserve Snapshots"), required=False, initial=True,
        help_text=_("Enforces migration of the share snapshots to the "
                    "destination. If set to True, host-assisted migration will"
                    " not be attempted."))
    new_share_network = forms.ChoiceField(
        label=_("New share network to be set in migrated share"),
        required=False,
        help_text=_('Specify the new share network for the share. Do not '
                    'specify this parameter if the migrating share has to be '
                    'retained within its current share network.'))
    new_share_type = forms.ChoiceField(
        label=_("New share type to be set in migrating share"), required=False,
        help_text=_('Specify the new share type for the share. Do not specify '
                    'this parameter if the migrating share has to be retained '
                    'with its current share type.'))

    def __init__(self, request, *args, **kwargs):
        super(MigrationStart, self).__init__(request, *args, **kwargs)
        share_networks = manila.share_network_list(request)
        share_types = manila.share_type_list(request)
        dests = manila.pool_list(request)
        dest_choices = [('', '')] + [(d.name, d.name) for d in dests]
        st_choices = [('', '')] + [(st.id, st.name) for st in share_types]
        sn_choices = (
            [('', '')] +
            [(sn.id, sn.name or sn.id) for sn in share_networks])
        self.fields['host'].choices = dest_choices
        self.fields['new_share_type'].choices = st_choices
        self.fields['new_share_network'].choices = sn_choices

    def handle(self, request, data):
        share_name = _get_id_if_name_empty(data)
        try:
            manila.migration_start(
                request, self.initial['share_id'],
                force_host_assisted_migration=(
                    data['force_host_assisted_migration']),
                writable=data['writable'],
                preserve_metadata=data['preserve_metadata'],
                preserve_snapshots=data['preserve_snapshots'],
                nondisruptive=data['nondisruptive'],
                dest_host=data['host'],
                new_share_network_id=data['new_share_network'],
                new_share_type_id=data['new_share_type'])

            messages.success(
                request,
                _('Successfully sent the request to migrate share: %s.')
                % share_name)
            return True
        except Exception:
            redirect = reverse("horizon:admin:shares:index")
            exceptions.handle(
                request, _("Unable to migrate share %s.") % share_name,
                redirect=redirect)
        return False


class MigrationForms(forms.SelfHandlingForm):
    name = forms.CharField(
        label=_("Share Name"), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    share_id = forms.CharField(
        label=_("ID"), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))


class MigrationComplete(MigrationForms):

    def handle(self, request, data):
        share_name = _get_id_if_name_empty(data)
        try:
            manila.migration_complete(request, self.initial['share_id'])
            messages.success(
                request,
                _('Successfully sent the request to complete migration of '
                  ' share: %s.') % share_name)
            return True
        except Exception:
            exceptions.handle(request, _("Unable to complete migration "
                                         "of share %s.") % share_name)
        return False


class MigrationGetProgress(MigrationForms):

    def handle(self, request, data):
        share_name = _get_id_if_name_empty(data)
        try:
            result = manila.migration_get_progress(request,
                                                   self.initial['share_id'])
            progress = result[1]
            messages.success(
                request,
                _('Migration of share %(name)s is at %(progress)s percent.') %
                {'name': share_name, 'progress': progress['total_progress']})
            return True
        except Exception:
            exceptions.handle(request, _("Unable to obtain progress of "
                                         "migration of share %s at this "
                                         "moment.") % share_name)
        return False


class MigrationCancel(MigrationForms):

    def handle(self, request, data):
        share_name = _get_id_if_name_empty(data)
        try:
            manila.migration_cancel(request, self.initial['share_id'])
            messages.success(
                request,
                _('Successfully sent the request to cancel migration of '
                  ' share: %s.') % share_name)
            return True
        except Exception:
            exceptions.handle(request, _("Unable to cancel migration of share"
                                         " %s at this moment.") % share_name)
        return False


class ManageShare(forms.SelfHandlingForm):
    name = forms.CharField(
        max_length=255, label=_("Share Name"), required=False,
        help_text=_("Share name to be assigned"))
    description = forms.CharField(
        max_length=255, label=_("Description"), required=False,
        widget=forms.Textarea(
            attrs={'class': 'modal-body-fixed-width', 'rows': 4}))

    host = forms.CharField(
        max_length=255, label=_("Host of share"), required=True,
        help_text=_(
            "Host where share is located, example: some.host@driver[#pool]"))
    export_location = forms.CharField(
        max_length=255, label=_("Export location"), required=True,
        help_text=_("Export location of share. Example for NFS: "
                    "1.2.3.4:/path/to/share"))

    protocol = forms.ChoiceField(label=_("Share Protocol"), required=True)

    share_type = forms.ChoiceField(label=_("Share Type"), required=True)

    driver_options = forms.CharField(
        max_length=255, required=False,
        label=_("Driver options ('volume_id' for Generic driver, etc...)"),
        help_text=_("key=value pairs per line can be set"),
        widget=forms.Textarea(
            attrs={'class': 'modal-body-fixed-width', 'rows': 2}))
    is_public = forms.BooleanField(
        label=_("Public"), required=False, initial=False,
        help_text=("Defines whether this share is available for all or not."))

    def __init__(self, request, *args, **kwargs):
        super(ManageShare, self).__init__(request, *args, **kwargs)
        share_types = manila.share_type_list(request)
        # NOTE(vponomaryov): choose only those share_types that have spec
        # 'driver_handles_share_servers' set to 'False' value or alias of it.
        dhss_key = 'driver_handles_share_servers'
        st_choices = [('', ''), ]
        for st in share_types:
            dhss = st.to_dict()['extra_specs'].get(dhss_key)
            if dhss and dhss.lower() in strutils.FALSE_STRINGS:
                st_choices.append((st.name, st.name))
        self.fields['share_type'].choices = st_choices
        # NOTE(vkmc): choose only those share protocols that are enabled
        # FIXME(vkmc): this should be better implemented by having a
        # capabilities endpoint on the control plane.
        manila_features = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
        self.enabled_share_protocols = manila_features.get(
            'enabled_share_protocols',
            ['NFS', 'CIFS', 'GlusterFS', 'HDFS', 'CephFS', 'MapRFS'])
        self.fields['protocol'].choices = ([(' ', ' ')] +
                                           [(enabled_proto, enabled_proto)
                                           for enabled_proto in
                                           self.enabled_share_protocols])

    def handle(self, request, data):
        try:
            driver_options = data.get('driver_options') or {}
            driver_options_error_msg = _(
                "Got improper value for field 'driver_options'. "
                "Expected only pairs of key=value.")
            if driver_options and isinstance(driver_options, six.string_types):
                try:
                    set_dict, unset_list = utils.parse_str_meta(driver_options)
                    if unset_list:
                        raise ValidationError(message=driver_options_error_msg)
                    driver_options = set_dict
                except ValidationError as e:
                    self.api_error(e.messages[0])
                    return False
            elif not isinstance(driver_options, dict):
                self.api_error(driver_options_error_msg)
                return False

            manila.share_manage(
                request,
                service_host=data['host'],
                protocol=data['protocol'],
                export_path=data['export_location'],
                driver_options=driver_options,
                share_type=data['share_type'],
                name=data['name'],
                description=data['description'],
                is_public=data['is_public'])

            share_name = data.get('name', data.get('id'))
            messages.success(
                request,
                _('Successfully sent the request to manage share: %s')
                % share_name)
            return True
        except Exception:
            exceptions.handle(request, _("Unable to manage share"))
        return False


class UnmanageShare(forms.SelfHandlingForm):
    name = forms.CharField(
        label=_("Share Name"), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    host = forms.CharField(
        label=_("Host"), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    share_id = forms.CharField(
        label=_("ID"), required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        try:
            manila.share_unmanage(request, self.initial['share_id'])
            messages.success(
                request,
                _('Successfully sent the request to unmanage share: %s')
                % data['name'])
            return True
        except Exception:
            exceptions.handle(request, _("Unable to unmanage share."))
        return False
