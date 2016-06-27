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

"""
Views for managing shares.
"""

from django.core.urlresolvers import reverse
from django.forms import ValidationError  # noqa
from django.template.defaultfilters import filesizeformat  # noqa
from django.utils.translation import ugettext_lazy as _
import six

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils.memoized import memoized  # noqa

from manila_ui.api import manila
from manila_ui.dashboards import utils
from openstack_dashboard.api import nova
from openstack_dashboard.usage import quotas


class CreateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Name"))
    description = forms.CharField(
        label=_("Description"), required=False,
        widget=forms.Textarea(attrs={'rows': 3}))
    share_proto = forms.ChoiceField(label=_("Share Protocol"), required=True)
    size = forms.IntegerField(min_value=1, label=_("Size (GiB)"))
    share_type = forms.ChoiceField(
        label=_("Share Type"), required=True,
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'sharetype'}))
    availability_zone = forms.ChoiceField(
        label=_("Availability Zone"),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateForm, self).__init__(request, *args, **kwargs)
        share_protos = ('NFS', 'CIFS', 'GlusterFS', 'HDFS', 'CephFS')
        share_networks = manila.share_network_list(request)
        share_types = manila.share_type_list(request)
        self.fields['share_type'].choices = (
            [("", "")] + [(st.name, st.name) for st in share_types])
        availability_zones = nova.availability_zone_list(request)
        self.fields['availability_zone'].choices = (
            [("", "")] +
            [(az.zoneName, az.zoneName) for az in availability_zones])

        self.sn_field_name_prefix = 'share-network-choices-'
        for st in share_types:
            extra_specs = st.get_keys()
            dhss = extra_specs.get('driver_handles_share_servers')
            # NOTE(vponomaryov): Set and tie share-network field only for
            # share types with enabled handling of share servers.
            if (isinstance(dhss, six.string_types) and
                    dhss.lower() in ['true', '1']):
                sn_choices = (
                    [('', '')] +
                    [(sn.id, sn.name or sn.id) for sn in share_networks])
                sn_field_name = self.sn_field_name_prefix + st.name
                sn_field = forms.ChoiceField(
                    label=_("Share Network"), required=True,
                    choices=sn_choices,
                    widget=forms.Select(attrs={
                        'class': 'switched',
                        'data-switch-on': 'sharetype',
                        'data-sharetype-%s' % st.name: _("Share Network"),
                    }))
                self.fields[sn_field_name] = sn_field

        self.fields['share_source_type'] = forms.ChoiceField(
            label=_("Share Source"), required=False,
            widget=forms.Select(
                attrs={'class': 'switchable', 'data-slug': 'source'}))
        self.fields['snapshot'] = forms.ChoiceField(
            label=_("Use snapshot as a source"),
            widget=forms.fields.SelectWidget(
                attrs={'class': 'switched',
                       'data-switch-on': 'source',
                       'data-source-snapshot': _('Snapshot')},
                data_attrs=('size', 'name'),
                transform=lambda x: "%s (%sGiB)" % (x.name, x.size)),
            required=False)
        self.fields['metadata'] = forms.CharField(
            label=_("Metadata"), required=False,
            widget=forms.Textarea(attrs={'rows': 4}))
        self.fields['is_public'] = forms.BooleanField(
            label=_("Make visible for all"), required=False,
            help_text=(
                "If set then all tenants will be able to see this share."))

        self.fields['share_proto'].choices = [(sp, sp) for sp in share_protos]
        if "snapshot_id" in request.GET:
            try:
                snapshot = self.get_snapshot(request,
                                             request.GET["snapshot_id"])
                self.fields['name'].initial = snapshot.name
                self.fields['size'].initial = snapshot.size
                self.fields['snapshot'].choices = ((snapshot.id, snapshot),)
                try:
                    # Set the share type from the original share
                    orig_share = manila.share_get(request, snapshot.share_id)
                    self.fields['share_type'].initial = orig_share.share_type
                except Exception:
                    pass
                self.fields['size'].help_text = _(
                    'Share size must be equal to or greater than the snapshot '
                    'size (%sGiB)') % snapshot.size
                del self.fields['share_source_type']
            except Exception:
                exceptions.handle(request,
                                  _('Unable to load the specified snapshot.'))
        else:
            source_type_choices = []

            try:
                snapshot_list = manila.share_snapshot_list(request)
                snapshots = [s for s in snapshot_list
                             if s.status == 'available']
                if snapshots:
                    source_type_choices.append(("snapshot",
                                                _("Snapshot")))
                    choices = [('', _("Choose a snapshot"))] + \
                              [(s.id, s) for s in snapshots]
                    self.fields['snapshot'].choices = choices
                else:
                    del self.fields['snapshot']
            except Exception:
                exceptions.handle(request, _("Unable to retrieve "
                                  "share snapshots."))

            if source_type_choices:
                choices = ([('no_source_type',
                             _("No source, empty share"))] +
                           source_type_choices)
                self.fields['share_source_type'].choices = choices
            else:
                del self.fields['share_source_type']

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()
        errors = [k for k in self.errors.viewkeys()]

        # NOTE(vponomaryov): skip errors for share-network fields that are not
        # related to chosen share type.
        for k in errors:
            st_name = k.split(self.sn_field_name_prefix)[-1]
            chosen_st = cleaned_data.get('share_type')
            if (k.startswith(self.sn_field_name_prefix) and
                    st_name != chosen_st):
                cleaned_data[k] = 'Not set'
                self.errors.pop(k, None)

        share_type = cleaned_data.get('share_type')
        if share_type:
            cleaned_data['share_network'] = cleaned_data.get(
                self.sn_field_name_prefix + share_type)

        return cleaned_data

    def handle(self, request, data):
        try:
            # usages = quotas.tenant_limit_usages(self.request)
            # availableGB = usages['maxTotalShareGigabytes'] - \
            #    usages['gigabytesUsed']
            # availableVol = usages['maxTotalShares'] - usages['sharesUsed']

            snapshot_id = None
            source_type = data.get('share_source_type', None)
            share_network = data.get('share_network', None)
            if (data.get("snapshot", None) and
                    source_type in [None, 'snapshot']):
                # Create from Snapshot
                snapshot = self.get_snapshot(request,
                                             data["snapshot"])
                snapshot_id = snapshot.id
                if (data['size'] < snapshot.size):
                    error_message = _('The share size cannot be less than the '
                                      'snapshot size (%sGiB)') % snapshot.size
                    raise ValidationError(error_message)
            else:
                if type(data['size']) is str:
                    data['size'] = int(data['size'])
            #
            # if availableGB < data['size']:
            #    error_message = _('A share of %(req)iGB cannot be created as '
            #                      'you only have %(avail)iGB of your quota '
            #                      'available.')
            #    params = {'req': data['size'],
            #              'avail': availableGB}
            #    raise ValidationError(error_message % params)
            # elif availableVol <= 0:
            #    error_message = _('You are already using all of your '
            #                      'available'
            #                      ' shares.')
            #    raise ValidationError(error_message)

            metadata = {}
            try:
                set_dict, unset_list = utils.parse_str_meta(data['metadata'])
                if unset_list:
                    msg = _("Expected only pairs of key=value.")
                    raise ValidationError(message=msg)
                metadata = set_dict
            except ValidationError as e:
                self.api_error(e.messages[0])
                return False
            share = manila.share_create(
                request,
                size=data['size'],
                name=data['name'],
                description=data['description'],
                proto=data['share_proto'],
                share_network=share_network,
                snapshot_id=snapshot_id,
                share_type=data['share_type'],
                is_public=data['is_public'],
                metadata=metadata,
                availability_zone=data['availability_zone'])
            message = _('Creating share "%s"') % data['name']
            messages.success(request, message)
            return share
        except ValidationError as e:
            self.api_error(e.messages[0])
            return False
        except Exception:
            exceptions.handle(request, ignore=True)
            self.api_error(_("Unable to create share."))
            return False

    @memoized
    def get_snapshot(self, request, id):
        return manila.share_snapshot_get(request, id)


class UpdateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Name"))
    description = forms.CharField(widget=forms.Textarea,
                                  label=_("Description"), required=False)
    is_public = forms.ChoiceField(
        choices=((None, 'Do not change share visibility'),
                 (False, "Make it 'Private'"), (True, "Make it 'Public'")),
        label=_("Visibility"), required=False,
        widget=forms.Select(
            attrs={'class': 'switched', 'data-slug': 'sharetype'}))

    def handle(self, request, data):
        share_id = self.initial['share_id']
        try:
            share = manila.share_get(self.request, share_id)
            manila.share_update(
                request, share, data['name'], data['description'],
                is_public=data['is_public'])
            message = _('Updating share "%s"') % data['name']
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:shares:index")
            exceptions.handle(request,
                              _('Unable to update share.'),
                              redirect=redirect)


class UpdateMetadataForm(forms.SelfHandlingForm):
    metadata = forms.CharField(widget=forms.Textarea,
                               label=_("Metadata"), required=False)

    def __init__(self, *args, **kwargs):
        super(UpdateMetadataForm, self).__init__(*args, **kwargs)
        meta_str = ""
        for k, v in self.initial["metadata"].iteritems():
            meta_str += "%s=%s\r\n" % (k, v)
        self.initial["metadata"] = meta_str

    def handle(self, request, data):
        share_id = self.initial['share_id']
        try:
            share = manila.share_get(self.request, share_id)
            set_dict, unset_list = utils.parse_str_meta(data['metadata'])
            if set_dict:
                manila.share_set_metadata(request, share, set_dict)
            if unset_list:
                manila.share_delete_metadata(request, share, unset_list)
            message = _('Updating share metadata "%s"') % share.name
            messages.success(request, message)
            return True
        except ValidationError as e:
            self.api_error(e.messages[0])
            return False
        except Exception:
            redirect = reverse("horizon:project:shares:index")
            exceptions.handle(request,
                              _('Unable to update share metadata.'),
                              redirect=redirect)


class AddRule(forms.SelfHandlingForm):
    access_type = forms.ChoiceField(
        label=_("Access Type"), required=True,
        choices=(('ip', 'ip'), ('user', 'user'), ('cert', 'cert'),
                 ('cephx', 'cephx')))
    access_level = forms.ChoiceField(
        label=_("Access Level"), required=True,
        choices=(('rw', 'read-write'), ('ro', 'read-only'),))
    access_to = forms.CharField(
        label=_("Access To"), max_length="255", required=True)

    def handle(self, request, data):
        share_id = self.initial['share_id']
        try:
            manila.share_allow(
                request, share_id,
                access_to=data['access_to'],
                access_type=data['access_type'],
                access_level=data['access_level'])
            message = _('Creating rule for "%s"') % data['access_to']
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:shares:manage_rules",
                               args=[self.initial['share_id']])
            exceptions.handle(
                request, _('Unable to add rule.'), redirect=redirect)


class ExtendForm(forms.SelfHandlingForm):
    name = forms.CharField(
        max_length="255", label=_("Share Name"),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False,
    )

    orig_size = forms.IntegerField(
        label=_("Current Size (GiB)"),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False,
    )

    new_size = forms.IntegerField(
        label=_("New Size (GiB)"),
    )

    def clean(self):
        cleaned_data = super(ExtendForm, self).clean()
        new_size = cleaned_data.get('new_size')
        orig_size = self.initial['orig_size']

        if new_size <= orig_size:
            message = _("New size must be greater than current size.")
            self._errors["new_size"] = self.error_class([message])
            return cleaned_data

        usages = quotas.tenant_limit_usages(self.request)
        availableGB = (usages['maxTotalShareGigabytes'] -
                       usages['totalShareGigabytesUsed'])
        if availableGB < (new_size - orig_size):
            message = _('Share cannot be extended to %(req)iGiB as '
                        'you only have %(avail)iGiB of your quota '
                        'available.')
            params = {'req': new_size, 'avail': availableGB + orig_size}
            self._errors["new_size"] = self.error_class([message % params])
        return cleaned_data

    def handle(self, request, data):
        share_id = self.initial['share_id']
        try:
            manila.share_extend(request, share_id, data['new_size'])
            message = _('Extend share "%s"') % data['name']
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:shares:index")
            exceptions.handle(request,
                              _('Unable to extend share.'),
                              redirect=redirect)
