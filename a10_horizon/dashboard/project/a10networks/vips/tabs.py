# Copyright 2015,  A10 Networks
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

import logging

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs


LOG = logging.getLogger(__name__)


# lbaasv2 api
try:
    from neutron_lbaas_dashboard.api import lbaasv2 as lbaasv2_api
except ImportError as ex:
    LOG.exception(ex)
    LOG.warning("Could not import lbaasv2 dashboard API")

import tables as p_tables
# import a10_horizon.dashboard.api.vips as a10api

# move to template constants
TABLE_TEMPLATE = "horizon/common/_detail_table.html"
DEFAULT_TEMPLATE = "horizon/common/_detail.html"


class ProjectHealthMonitorTab(tabs.TableTab):
    table_classes = (p_tables.ProjectHealthMonitorTable, )
    name = _("Health Monitors")
    slug = "a10healthmonitorstab"
    template_name = TABLE_TEMPLATE
    preload = False

    def get_projecthealthmonitortable_data(self):
        rv = []

        try:
            rv = lbaasv2_api.healthmonitor_list(self.request)
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(self.request, _("Unable to retrieve health monitor server list"))
        return rv


class ProjectPoolTab(tabs.TableTab):
    table_classes = (p_tables.ProjectPoolTable,)
    name = _("Pools")
    slug = "a10poolstab"
    template_name = TABLE_TEMPLATE
    preload = False

    def get_projectpooltable_data(self):
        rv = []

        try:
            rv = lbaasv2_api.pool_list(self.request)
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(self.tab_group.request,
                              _("Unable to retrieve LB pool list."))
        return rv


class ProjectListenerTab(tabs.TableTab):
    table_classes = (p_tables.ProjectListenerTable,)
    name = _("Listeners")
    slug = "a10listenerstab"
    template_name = TABLE_TEMPLATE
    preload = False

    def get_projectlistenertable_data(self):
        rv = []

        try:
            rv = lbaasv2_api.list_listeners(self.request)
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve listener list.'))
        return rv


class ProjectLoadbalancerTab(tabs.TableTab):
    table_classes = (p_tables.ProjectLoadbalancerTable,)
    name = _("Load Balancers")
    slug = "a10loadbalancerstab"
    template_name = TABLE_TEMPLATE
    preload = False

    def get_projectloadbalancertable_data(self):
        rv = []
        try:
            rv = lbaasv2_api.list_loadbalancers(self.request)
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve load balancer list.'))
        return rv


class VipsTab(tabs.TableTab):
    table_classes = (p_tables.VipTable,)
    name = _("VIPs")
    slug = "a10vipstab"
    template_name = TABLE_TEMPLATE
    preload = False

    def get_viptable_data(self):
        result = []

        try:
            listeners = lbaasv2_api.list_listeners(self.request)
            lbs = lbaasv2_api.list_loadbalancers(self.request)
            result = self._transform(listeners, lbs)
        except Exception as ex:
            LOG.exception(ex)
            result = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve VIP list.'))
        return result

    def _transform(self, listeners, lbs):
        rv = []

        for listener in listeners:
            candidate_lbs = [x for x in lbs if x.get("id") in
                             [y.get("id") for y in listener.get("loadbalancers")]]
            if len(candidate_lbs) > 0:
                lb = candidate_lbs[0]
                row = {
                    "id": lb.get("id"),
                    "name": listener.get("name"),
                    "protocol": listener.get("protocol"),
                    "protocol_port": listener.get("protocol_port"),
                    "vip_address": lb.get("vip_address"),
                    "provisioning_status": lb.get("provisioning_status"),
                    "op_status": lb.get("operating_status"),
                    "provider": lb.get("provider")
                }
                rv.append(row)

        return rv


class A10LBTabs(tabs.TabGroup):
    slug = "a10tabs"

    tabs = (VipsTab,
            ProjectLoadbalancerTab,
            ProjectListenerTab,
            ProjectPoolTab,
            ProjectHealthMonitorTab,)

    sticky = False
    show_single_tab = True


class MonitorDetailsTabs(tabs.TabGroup):
    slug = "a10monitordetailstabs"
    tabs = ()
    stick = False
    show_single_tab = True


class MemberDetailsTabs(tabs.TabGroup):
    slug = "a10memberdetailstabs"
    tabs = ()
    stick = False
    show_single_tab = True


class PoolDetailsTabs(tabs.TabGroup):
    slug = "a10pooldetailstabs"
    tabs = ()
    stick = False
    show_single_tab = True


class ListenerDetailsTabs(tabs.TabGroup):
    slug = "a10listenerdetailstabs"
    tabs = ()
    sticky = False
    show_single_tab = True


class LBDetailsTabs(tabs.TabGroup):
    slug = "a10lbdetailstabs"
    tabs = ()
    sticky = False
    show_single_tab = True
