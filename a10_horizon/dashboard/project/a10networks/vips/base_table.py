# Copyright (C) 2014-2016, A10 Networks Inc. All rights reserved.
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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

# lbaasv2 api
try:
    from neutron_lbaas_dashboard.api import lbaasv2 as lbaasv2_api
except ImportError as ex:
    LOG.exception(ex)
    LOG.error("Could not import lbaasv2 dashboard API")

import links
import display_transform


class HealthMonitorTableBase(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    type = tables.Column("type", verbose_name=_("Type"))
    pool = tables.Column(display_transform.links_from_hm_pools)
    delay = tables.Column("delay", verbose_name=_("Delay"), hidden=True)
    timeout = tables.Column("timeout", verbose_name=_("Timeout"), hidden=True)
    max_retries = tables.Column("max_retries", verbose_name=_("Max Retries"))
    admin_state_up = tables.Column(display_transform.transform_admin_state_up,
                                   verbose_name=_("Admin State"))
    monitor_summary = tables.Column(display_transform.healthmonitor_summary,
                                    verbose_name=_("Monitor Summary"))


    def get_object_id(self, datum):
        return datum.get("id")


    class Meta(object):
        name = "healthmonitortable"
        verbose_name = "healthmonitortable"
        table_actions = tuple()
        row_actions = tuple()


class MemberTableBase(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    name = tables.Column("name", verbose_name=_("Name"), link=links.link_member_detail_by_id)
    address = tables.Column("address", verbose_name=_("IP Address"))
    protocol_port = tables.Column("protocol_port",
                                  verbose_name=_("Protocol Port"))
    admin_state_up = tables.Column(display_transform.transform_admin_state_up,
                                   verbose_name=_("Admin State"))
    # TODO(mdurrant) - The function for this should look up cached subnets
    # and substitute the name. See how they do it elsewhere in Horizon.
    subnet_id = tables.Column("subnet_id", verbose_name=_("Subnet"))
    weight = tables.Column("weight", verbose_name=_("Weight"))
    pool_id = tables.Column("pool_id", verbose_name=_("Pool ID"), hidden=True)

    def get_object_id(self, datum):
        return datum.get("id")


    class Meta(object):
        name = "membertable"
        verbose_name = "membertable"
        table_actions = tuple()
        row_actions = tuple()


class PoolTableBase(tables.DataTable):
    """
    Read only pool table, no actions.
    """
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    name = tables.Column("name", verbose_name=_("Name"), link=links.link_pool_detail_by_id)
    description = tables.Column("description", verbose_name=_("Description"))
    protocol = tables.Column("protocol", verbose_name=_("Protocol"))
    lb_algorithm = tables.Column("lb_algorithm", verbose_name=_("Algorithm"))
    admin_state_up = tables.Column(display_transform.transform_admin_state_up,
                                   verbose_name=_("Admin State"))
    session_persistence = tables.Column(display_transform.transform_session_persistence,
                                        verbose_name=_("Session Persistence"))
    health_monitor_id = tables.Column(display_transform.display_health_monitor, verbose_name=_("Health Monitor"),
                                      link=links.link_hm_detail_from_pool)

    def get_object_id(self, datum):
        return datum.get("id")

    class Meta(object):
        name = "pooltable"
        verbose_name = "pooltable"
        table_actions = tuple()
        row_actions = tuple()



class ListenerTableBase(tables.DataTable):
    """
    Read only listener table, no actions
    """
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    loadbalancer_id = tables.Column("loadbalancer_id",
                                    verbose_name=_("Loadbalancer ID"), hidden=True)
    name = tables.Column("name", verbose_name=_("Name"), link=links.link_listener_detail_by_id)
    description = tables.Column("description", verbose_name=_("Description"))
    protocol = tables.Column("protocol", verbose_name=_("Protocol"))
    protocol_port = tables.Column("protocol_port", verbose_name=_("Port"))
    connection_limit = tables.Column(display_transform.transform_connection_limit, verbose_name=_("Connection Limit"))
    admin_state_up = tables.Column(display_transform.transform_admin_state_up, verbose_name=_("Admin State"))

    def get_object_id(self, datum):
        return datum.get("id")

    class Meta(object):
        name = "listenertable"
        verbose_name = "listenertable"
        table_actions = tuple()
        row_actions = tuple()


class LoadbalancerTableBase(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    tenant_id = tables.Column("tenant_id", verbose_name=_("Tenant ID"), hidden=True)
    name = tables.Column("name", verbose_name=_("Name"), link=links.link_loadbalancer_detail_by_id)
    description = tables.Column("description", verbose_name=_("Description"))
    vip_address = tables.Column("vip_address", verbose_name=_("VIP Address"))
    vip_subnet_id = tables.Column("vip_subnet_id", verbose_name=_("VIP Subnet"))
    operating_status = tables.Column("operating_status", verbose_name=_("Operating Status"))
    provisioning_status = tables.Column("provisioning_status", verbose_name=_("Provisioning Status"))

    def get_object_id(self, datum):
        return datum.get("id")

    class Meta(object):
        name = "loadbalancertable"
        verbose_name = "loadbalancertable"
        table_actions = tuple()
        row_actions = tuple()


class DeleteActionBase(tables.DeleteAction):
    def __init__(self, data_single, data_plural, **kwargs):
        super(DeleteAction, self).__init__(**kwargs)

        self.data_single = kwargs.get("data_single")
        self.data_plural = "{0}s".format(self.data_single)
        self.verb_present = kwargs.get("verb_present", "Delete")
        self.verb_past = kwargs.get("verb_past", "Scheduled Deletion of")
