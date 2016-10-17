#    Copyright 2015, eBay Inc.
#    Portions Copyright 2014-2016 A10 Networks, Inc.
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

from __future__ import absolute_import

# from django.utils.translation import ugettext_lazy as _
import logging
# from horizon import messages

from openstack_dashboard.api import neutron

LOG = logging.getLogger(__name__)
neutronclient = neutron.neutronclient


class LBDetails(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron load balancer vip."""

    def __init__(self, vip, listener=None, pool=None, members=None,
                 monitors=None, profile_name=None, cert=None, key=None,
                 chain=None):
        vip['pool'] = pool
        pool['members'] = members
        pool['monitors'] = monitors
        # vip['cert_name'] = cert_name
        vip['listener'] = listener
        vip['cert'] = cert
        vip['key'] = key
        vip['chain'] = chain
        vip['profile_name'] = profile_name
        super(LBDetails, self).__init__(vip)

    class AttributeDict(dict):

        def __getattr__(self, attr):
            return self[attr]

        def __setattr__(self, attr, value):
            self[attr] = value

    def convert_status(self, value):
        return "Enabled" if value else "Disabled"

    def readable(self, request=None):

        pFormatted = {'id': self.id,
                      'name': self.name,
                      'dns_name': self.name,
                      # 'lb_method': self.lb_method,
                      'description': self.description,
                      # 'protocol': self.protocol,
                      'address': self.vip_address,
                      # 'port': self.port,
                      'enabled': self.convert_status(self.admin_state_up),
                      'use_common_cert': False,
                      'provisioning_status': self.provisioning_status,
                      'operating_status': self.operating_status,
                      # 'monitor' : self.monitor
                      }

        # status_string = 'vip: %s' % self['status'].lower()
        pFormatted['status'] = 'na'

        # if self.profile_name:
        #     try:
        #         if self.profile_name.upper() ==
        #          _construct_common_cert_profile_name(request).upper():
        #             pFormatted['use_common_cert'] = True
        #             pFormatted['cert_name'] = self.profile_name
        #         else:
        #             pFormatted['use_common_cert'] = False
        #             pFormatted['cert_name'] = self.profile_name
        #             pFormatted['cert'] = self.cert
        #             pFormatted['private_key'] = self.key
        #             pFormatted['chain_cert'] = self.chain
        #     except Exception as e:
        #         LOG.error("unable to read cert")

        if self.listener is not None:
            try:
                listener = self.AttributeDict(self.listener)
                pFormatted['protocol'] = listener.protocol
                pFormatted['port'] = listener.protocol_port
            except Exception:
                pass

        if self.pool is not None:
            try:
                pool = self.AttributeDict(self.pool)
                # status_string = '%s \n pool: %s' % (pFormatted['status'],
                # pool['status'].lower())
                # pFormatted['status'] = status_string
                pFormatted['pool'] = pool
                pFormatted['pool_id'] = pool.id
                pFormatted['lb_method'] = pool.lb_algorithm

                if pool.members is not None:
                    try:
                        ips = []
                        pool_members = []
                        for m in pool.members:
                            member = self.AttributeDict(m)
                            pFormatted['instance_port'] = member.protocol_port

                            pool_member = member
                            pool_member.port = member.protocol_port
                            pool_members.append(pool_member)

                            ips.append(member.address)
                        pFormatted['pool']['members'] = pool_members
                        pFormatted['members'] = ips
                    except Exception:
                        pass  # ignore

                if pool.monitors is not None:
                    try:
                        for m in pool.monitors:
                            monitor = self.AttributeDict(m)
                            # monitor_status =_get_monitor_status(pool['id'],m)
                            # status_string = '%s \n monitor: %s' %
                            # (pFormatted['status'], monitor_status.lower())
                            # pFormatted['status'] = status_string
                            interval = int(monitor.delay)
                            # timeout = int(monitor.timeout)
                            retry = int(monitor.max_retries)
                            monitor_type = 'http-ecv'
                            # if monitor.name.upper() in basic_monitors:
                            # monitor_type = monitor.name
                            monitor_type = monitor.name
                            pFormatted['pool']['monitor'] = monitor_type
                            pFormatted['monitor'] = monitor_type
                            pFormatted['interval'] = interval
                            pFormatted['timeout'] = retry
                            pFormatted['send'] = monitor.url_path \
                                if hasattr(monitor, 'url_path') else ''
                            pFormatted['receive'] = monitor.response_string \
                                if hasattr(monitor, 'response_string') else ''
                            break
                    except Exception:
                        pass  # ignore
            except Exception:
                pass  # ignore

        format_fields = {
            "cert_name": "",
            "cert": "",
            "private_key": "",
            "chain_cert": "",
            "pool_id": "UNKNOWN",
            "lb_method": "UNKNOWN",
            "monitor": "None",
            "interval": 1,
            "timeout": 1,
            "send": None,
            "receive": None,
            "members": [],
            "instance_port": "",
        }

        for x in format_fields.keys():
            if x not in pFormatted:
                pFormatted[x] = format_fields.get(x)

        return self.AttributeDict(pFormatted)


class LoadBalancer(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron load balancer member."""

    def __init__(self, apiresource):
        super(LoadBalancer, self).__init__(apiresource)


class Listener(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron load balancer member."""

    def __init__(self, apiresource):
        super(LoadBalancer, self).__init__(apiresource)


class Pool(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron load balancer pool."""

    def __init__(self, apiresource):
        # if 'provider' not in apiresource:
        #     apiresource['provider'] = None
        super(Pool, self).__init__(apiresource)


class Member(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron load balancer member."""

    def __init__(self, apiresource):
        super(Member, self).__init__(apiresource)


class HealthMonitor(neutron.NeutronAPIDictWrapper):

    """Wrapper for neutron load balancer pool health monitor."""

    def __init__(self, apiresource):
        super(HealthMonitor, self).__init__(apiresource)


class LBStats(neutron.NeutronAPIDictWrapper):

    def __init__(self, apiresource):
        super(LBStats, self).__init__(apiresource)


# TODO(mdurrant) - Ensure all calls to this are gone
# You can build an LB using the constituent object calls.
def create_loadbalancer_full(request, **kwargs):
    loadbalancer_body = _build_loadbalancer(kwargs)
    listener_body = _build_listener(kwargs)
    pool_body = _build_pool(kwargs)
    member_body = _build_member(kwargs)
    health_monitor_body = _build_monitor(kwargs)

    # These actions need to be rolled back if any of them fail.
    try:
        client = neutronclient(request)
        loadbalancer = client.create_loadbalancer(loadbalancer_body).get('loadbalancer')
        listener_body['listener']['loadbalancer_id'] = loadbalancer['id']
        listener = client.create_listener(listener_body).get('listener')
        pool["pool"]["listener_id"] = listener.get("id")
        pool = client.create_lbaas_pool(pool_body).get('pool')

        member_body['member']['pool_id'] = pool['id']
        health_monitor_body['health_monitor']['pool_id'] = pool['id']

        health_monitor = client.create_lbaas_healthmonitor(
            health_monitor_body).get('health_monitor')
        member = client.create_lbaas_member(member_body).get('member')
    except Exception:
        raise Exception(_("Could not create full loadbalancer."))
    return [LBDetails(loadbalancer, listener, pool, member, health_monitor)]


def delete_loadbalancer(request, lb_id):
    neutronclient(request).delete_loadbalancer(lb_id)


def create_loadbalancer(request, lb):
    lb = neutronclient(request).create_loadbalancer(lb)
    return lb.get("loadbalancer", {})


def get_loadbalancer(request, lb_id):
    lb = neutronclient(request).show_loadbalancer(lb_id)
    return lb.get("loadbalancer")


def update_loadbalancer(request, lbid, **kwargs):
    lb = neutronclient(request).update_loadbalancer(lbid, kwargs).get("loadbalancer")
    return lb


def get_loadbalancer_status(request, id):
    return neutronclient(request).retrieve_loadbalancer_status(id).get("statuses", {})


def get_loadbalancer_stats(request, id):
    return neutronclient(request).retrieve_loadbalancer_stats(id).get("stats", {})


def list_listeners(request, **kwargs):
    listeners = neutronclient(request).list_listeners(**kwargs)
    return listeners.get("listeners", [])


def create_listener(request, listener):
    listener = neutronclient(request).create_listener(listener)
    return listener.get("listener", {})


def delete_listener(request, listener_id):
    success = False
    try:
        neutronclient(request).delete_listener(listener_id)
        success = True
    except Exception as ex:
        LOG.exception(ex)
    return success


def show_listener(request, id):
    listener = neutronclient(request).show_listener(id)
    return listener.get("listener")


def update_listener(request, id, **listener):
    listener = neutronclient(request).update_listener(id, listener).get("listener")
    return listener


def list_loadbalancers(request, **kwargs):
    lbs = neutronclient(request).list_loadbalancers(**kwargs) or {"loadbalancers": []}
    return lbs.get("loadbalancers", [])


def show_loadbalancer(request, lbaas_loadbalancer, **kwargs):
    lb = neutronclient(request).show_loadbalancer(lbaas_loadbalancer,
                                                  **kwargs)
    if not lb:
        return
    loadbalancer = lb.get('loadbalancer')
    listeners = loadbalancer.get('listeners', [])

    # TODO(mdurrant) - This is a slow way to retrieve an LB. Use the status tree.
    for viplistener in listeners:
        # initialize empty defaults so we can return a complete, accurate data structure
        # ... without using locals().
        listener = {}
        pool = {}
        health_monitor = {}
        members = []

        listener = neutronclient(request).show_listener(viplistener.get('id'), **kwargs)
        # Load balancers can exist without listeners...
        if not listener:
            listener = {"listener": {}}

        listener = listener.get('listener')
        # ... and listeners can exist without pools ...
        pool = neutronclient(request).show_lbaas_pool(listener.get('default_pool_id'), **kwargs)
        if not pool:
            continue
        pool = pool.get('pool')
        # ... and not all pools have health monitors...
        health_monitor = None
        if pool.get('healthmonitor_id'):
            health_monitor = neutronclient(request).\
                show_lbaas_healthmonitor(pool.get('healthmonitor_id'),
                                         **kwargs)
            health_monitor = health_monitor.get('healthmonitor')
        # ... or members.
        members = neutronclient(request).list_lbaas_members(listener.get('default_pool_id'),
                                                            **kwargs)

    return LBDetails(lb.get('loadbalancer'), listener, pool, members,
                     health_monitor)


def loadbalancer_delete(request, lb_id):
    success = False
    try:
        neutronclient(request).delete_loadbalancer(lb_id)
        success = True
    except Exception as ex:
        LOG.exception(ex)
    return success


def pool_create(request, **kwargs):
    """
        Create the specified pool

        :param request: request context
        :param protocol: Pool protocol (HTTP/HTTPS/TCP)
        :param lb_algorithm: load balancing algorithm
        :param listener_id: Listener ID of Pool
        :param tenant_id: (optional) Create pool for the specified tenant (admin only - call will fail)
        :param name: (optional) Pool name (default: "")
        :param description: (optional) Pool description (default: "")
        :param admin_state_up: (optional) Admin state flag (default on/True)
        :param session_persistence: (optional) Session persistence. default value is empty dict
        :param session_persistence.type: APP_COOKIE, HTTP_COOKIE, SOURCE_IP
        :param session_persistence.cookie_name: Only specified for APP_COOKIE
    """

    body = {'pool': {
        'name': kwargs.get('name'),
        'description': kwargs.get('description'),
        'listener_id': kwargs['listener_id'],
        'lb_algorithm': kwargs['lb_algorithm'],
        'protocol': kwargs['protocol'],
        'admin_state_up': kwargs.get('admin_state_up', True),
        'session_persistence': kwargs.get('session_persistence', {})
    }}

    if "tenant_id" in kwargs and kwargs["tenant_id"] is not None:
        body["pool"]["tenant_id"] = kwargs.get("tenant_id")

    pool = neutronclient(request).create_lbaas_pool(body).get('pool')
    return pool


def pool_list(request, **kwargs):
    return _pool_list(request, **kwargs)


def _pool_list(request, **kwargs):
    # This is the v1 API
    pools = neutronclient(request).list_lbaas_pools(**kwargs).get('pools')
    return pools


def pool_get(request, pool_id):
    return _pool_get(request, pool_id, expand_resource=True)


def _pool_get(request, pool_id, expand_resource=False):
    try:
        pool = neutronclient(request).show_lbaas_pool(pool_id).get('pool')
    except Exception as ex:
        LOG.exception(ex)
        return None

    return pool


def pool_update(request, pool_id, **kwargs):
    pool = neutronclient(request).update_lbaas_pool(pool_id, kwargs).get('pool')
    return pool


def pool_delete(request, pool):
    try:
        neutronclient(request).delete_lbaas_pool(pool)
        return True
    except Exception as ex:
        LOG.exception(ex)


def member_create(request, pool_id, member):
    """Create a load balance member
    """
    member = neutronclient(request).create_lbaas_member(pool_id, member).get('member')
    return member


def member_list(request, pool_id, **kwargs):
    return _member_list(request, pool_id, **kwargs)


def _member_list(request, pool_id, **kwargs):
    members = neutronclient(requargsest).list_lbaas_members(pool_id, **kwargs).get('members')
    return [m for m in members]


def member_get(request, pool_id, member_id, **kwargs):
    rv = neutronclient(request).show_lbaas_member(member_id, pool_id, **kwargs).get('member')
    rv["pool_id"] = pool_id
    return rv


def member_update(request, pool_id, member_id, **kwargs):
    member = neutronclient(request).update_lbaas_member(member_id, pool_id, kwargs)
    return member


def member_delete(request, pool_id, member_id):
    neutronclient(request).delete_lbaas_member(pool_id, member_id)


def healthmonitor_create(request, **kwargs):
    body = {"healthmonitor": {
        "pool_id": kwargs["pool_id"],
        "type": kwargs["type"],
        "delay": kwargs["delay"],
        "timeout": kwargs["timeout"],
        "max_retries": kwargs["max_retries"],
        "admin_state_up": kwargs.get("admin_state_up", False)
    }}

    # if HTTP monitor, set the right params
    if "http" in body["healthmonitor"]["type"]:
        body["healthmonitor"]["http_method"] = kwargs.get("http_method"),
        body["healthmonitor"]["url_path"] = kwargs.get("url_path"),
        body["healthmonitor"]["expected_codes"] = kwargs.get("expected_codes", [200, 201, 202])

    healthmonitor = neutronclient(request).create_lbaas_healthmonitor(body).get("healthmonitor")

    return healthmonitor


def healthmonitor_get(request, id):
    hm = neutronclient(request).show_lbaas_healthmonitor(id)
    return hm


def healthmonitor_delete(request, id):
    neutronclient(request).delete_lbaas_healthmonitor(id)


def healthmonitor_update(request, id, **kwargs):
    hm = neutronclient(request).update_lbaas_healthmonitor(id, kwargs)
    return hm


def healthmonitor_list(request, **kwargs):
    rv = []
    # TODO(mdurrant) - Look into the other side of this call
    # What does returning a generator get us?
    expand_pools = kwargs.get("expand_pools", False)
    list_result = neutronclient(request).list_lbaas_healthmonitors(kwargs)

    # If kwargs == {}, we get a generator expression back. This allows for paging.
    # If kwargs == None, we get a list back. Yeah.
    if kwargs is not None:
        hms = next(list_result, [{}])

    return [x for x in hms.get("healthmonitors", [])]


def _build_loadbalancer(body):
    return {'loadbalancer': {
            'name': body['name'],
            'description': body['description'],
            'vip_subnet_id': body['subnet_id'],
            'admin_state_up': body['admin_state_up'],
            'vip_address': body['address'],
            }}


def _build_listener(body):
    # TODO(mdurrant): These all need sensible defaults
    return {'listener': {
        'name': body['listener_name'],
        'description': body['listener_desc'],
        'protocol': body['protocol'],
        'protocol_port': body['protocol_port'],
        'default_tls_container_id': None,
        'sni_container_ids': [],
        'connection_limit': body.get("connection_limit", -1),
        'admin_state_up': body['admin_state_up'],
        'loadbalancer_id': None}}


def _build_pool(body):
    return {'pool': {
        'name': body['name'],
        'description': body['description'],
        'protocol': body['protocol'],
        'lb_algorithm': body['lb_algorithm'],
        'admin_state_up': body['admin_state_up'],
        'listener_id': body['listener_id']
    }}


def _build_member(body):
    rv = {'member': {
        'pool_id': body['pool_id'],
        'address': body['address'],
        'protocol_port': body['protocol_port'],
        'admin_state_up': body['admin_state_up'],
        'pool_id': None
    }}

    if body.get('weight'):
        rv['member']['weight'] = body['weight']

    return rv


def _build_monitor(body):
    monitor_type = body['type'].upper()

    rv = {'healthmonitor': {
        'tenant_id': body['tenant_id'],
        'type': monitor_type,
        'delay': body['delay'],
        'timeout': body['timeout'],
        'max_retries': body['max_retries'],
        'admin_state_up': body['admin_state_up'],
        'pool_id': None
    }}

    # Only HTTP monitor types have HTTP method, url paths, and expected codes.
    if monitor_type in ['HTTP', 'HTTPS']:
        rv["healthmonitor"]['http_method'] = body['http_method']
        rv["healthmonitor"]['url_path'] = body['url_path']
        rv["healthmonitor"]['expected_codes'] = body['expected_codes']

    return rv
