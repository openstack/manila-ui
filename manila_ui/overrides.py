import functools
import sys

from horizon import exceptions

from manila_ui.api import manila

from openstack_dashboard.usage import quotas
from openstack_dashboard.api import base


def wrap(orig_func):
    """ decorator to wrap an existing function
        Modified post from http://downgra.de/2009/05/16/python-monkey-patching/
        to work with functions
        e.g.

        @wrap(quotas.tenant_limit_usages)
        def tenant_limit_usages(orig, self):
            limits = orig(request)
            limits['disksUsed'] = 100
            return limits

        the first parameter of the new function is the the original,
        overwritten function ('orig').
    """

    def outer(new_func):
        @functools.wraps(orig_func)
        def wrapper(*args, **kwargs):
            return new_func(orig_func, *args, **kwargs)
        # Replace the original function in the module with the wrapper
        orig_module = sys.modules[orig_func.__module__]
        setattr(orig_module, orig_func.__name__, wrapper)
        return wrapper
    return outer


# All public methods in openstack_dashboard.usage.quotas are hardcoded to
# only look at a fixed set of services (nova, cinder, etc.).  In order to
# incorporate manila quotas and usage, all public functions must be
# monkey-patched to add that information in.

MANILA_QUOTA_FIELDS = (
    "shares",
    "snapshots",
    "gigabytes",
    "share_networks",
)

quotas.QUOTA_FIELDS = quotas.QUOTA_FIELDS + MANILA_QUOTA_FIELDS

def _get_manila_disabled_quotas(request):
    disabled_quotas = []
    if not base.is_service_enabled(request, 'share'):
        disabled_quotas.extend(MANILA_QUOTA_FIELDS)

    return disabled_quotas


def _get_manila_quota_data(request, method_name, disabled_quotas=None,
                           tenant_id=None):
    if not tenant_id:
        tenant_id = request.user.tenant_id
    if 'shares' not in disabled_quotas:
        return getattr(manila, method_name)(request, tenant_id)
    else:
        return None

@wrap(quotas.get_default_quota_data)
def get_default_quota_data(f, request, disabled_quotas=None, tenant_id=None):
    qs = f(request, disabled_quotas, tenant_id)
    manila_quota = _get_manila_quota_data(request, "default_quota_get",
                                          disabled_quotas=disabled_quotas,
                                          tenant_id=tenant_id)
    if manila_quota:
        qs.add(manila_quota)
    return qs


@wrap(quotas.get_tenant_quota_data)
def get_tenant_quota_data(f, request, disabled_quotas=None, tenant_id=None):
    qs = f(request, disabled_quotas, tenant_id)
    manila_quota = _get_manila_quota_data(request, "tenant_quota_get",
                                          disabled_quotas=disabled_quotas,
                                          tenant_id=tenant_id)
    if manila_quota:
        qs.add(manila_quota)
    return qs


@wrap(quotas.get_disabled_quotas)
def get_disabled_quotas(f, request):
    disabled_quotas = f(request)
    disabled_quotas.extend(_get_manila_disabled_quotas(request))
    return disabled_quotas


@wrap(quotas.tenant_quota_usages)
def tenant_quota_usages(f, request, tenant_id=None):

    usages = f(request, tenant_id)

    if 'shares' not in _get_manila_disabled_quotas(request):
        shares = manila.share_list(request)
        snapshots = manila.share_snapshot_list(request)
        sn_l = manila.share_network_list(request)
        gig_s = sum([int(v.size) for v in shares])
        gig_ss = sum([int(v.size) for v in snapshots])
        usages.tally('gigabytes', gig_s + gig_ss)
        usages.tally('shares', len(shares))
        usages.tally('snapshots', len(snapshots))
        usages.tally('share_networks', len(sn_l))

    return usages


@wrap(quotas.tenant_limit_usages)
def tenant_limit_usages(f, request):

    limits = f(request)

    if base.is_service_enabled(request, 'share'):
        try:
            limits.update(manila.tenant_absolute_limits(request))
            shares = manila.share_list(request)
            snapshots = manila.share_snapshot_list(request)
            total_s_size = sum([getattr(share, 'size', 0) for share in shares])
            total_ss_size = sum([getattr(ss, 'size', 0) for ss in snapshots])
            limits['totalGigabytesUsed'] = total_s_size + total_ss_size
            limits['totalSharesUsed'] = len(shares)
            limits['totalSnapshotsUsed'] = len(snapshots)
        except Exception:
            msg = _("Unable to retrieve share limit information.")
            exceptions.handle(request, msg)

    return limits
