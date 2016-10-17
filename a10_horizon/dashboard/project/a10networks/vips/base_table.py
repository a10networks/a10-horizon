#    Copyright (C) 2014-2016, A10 Networks Inc. All rights reserved.
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
from horizon import tables

import logging

LOG = logging.getLogger(__name__)

import display_transform
import links


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
    health_monitor_id = tables.Column(display_transform.display_health_monitor,
                                      verbose_name=_("Health Monitor"),
                                      link=links.link_hm_detail_from_pool)
    member_count = tables.Column(display_transform.member_count, verbose_name=_("# of Members"))

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
    connection_limit = tables.Column(display_transform.transform_connection_limit,
                                     verbose_name=_("Connection Limit"))
    admin_state_up = tables.Column(display_transform.transform_admin_state_up,
                                   verbose_name=_("Admin State"))

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
    name = tables.Column("name", verbose_name=_("Name"),
                         link=links.link_loadbalancer_detail_by_id)
    description = tables.Column("description", verbose_name=_("Description"))
    vip_address = tables.Column("vip_address", verbose_name=_("VIP Address"))
    vip_subnet_id = tables.Column("vip_subnet_id", verbose_name=_("VIP Subnet"))
    operating_status = tables.Column("operating_status", verbose_name=_("Operating Status"))
    provisioning_status = tables.Column("provisioning_status",
                                        verbose_name=_("Provisioning Status"))

    def get_object_id(self, datum):
        return datum.get("id")

    class Meta(object):
        name = "loadbalancertable"
        verbose_name = "loadbalancertable"
        table_actions = tuple()
        row_actions = tuple()


class CertificateTableBase(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    name = tables.Column("name", verbose_name=_("Name"))
    description = tables.Column("description", verbose_name=_("Description"))
    cert_data = tables.Column("cert_data", verbose_name=_("Certificate Data"), hidden=True)
    key_data = tables.Column("key_data", verbose_name=_("Key Data"), hidden=True)
    intermediate_data = tables.Column("intermediate_data", verbose_name=_("Intermediate Data"), hidden=True)

    def get_object_id(self, datum):
        return datum.get("id")

    class Meta(object):
        name = "certificatetable"
        verbose_name = "certificate"
        table_action = tuple()
        row_actions = tuple()
