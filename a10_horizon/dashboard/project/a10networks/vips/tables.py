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

LOG = logging.getLogger(__name__)

import base_table as base
import links


URL_PREFIX = "horizon:project:a10vips:"
SUCCESS_URL = URL_PREFIX + "index"


def name_link(datum):
    return reverse_lazy("")

# obj_type:
allow_delete_functions = {
    "pool": lambda row: len(row.get("members")) == 0 and not row.get("healthmonitor_id"),
    "healthmonitor": lambda row: len(row.get("pools", [])) > 0,
    "loadbalancer": lambda row: len(row.get("listeners")) == 0,
    "listener": lambda row: not row.get("default_pool_id", False),
    "member": lambda row: True,
    "certificate": lambda row: True,
}


def allow_delete(obj_type, obj, default=True):
    allow_method = allow_delete_functions.get(obj_type)
    return allow_method(obj) if allow_method else default


class CreateVipLink(tables.LinkAction):
    name = "createvip"
    verbose_name = _("Create VIP")
    url = URL_PREFIX + "create"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = ("network",)  # FIXME(mdurrant) - A10-specific policies?
    success_url = SUCCESS_URL


class CreateLoadBalancerLink(tables.LinkAction):
    name = "createloadbalancer"
    verbose_name = _("Create Load Balancer")
    url = URL_PREFIX + "createlb"
    classes = ("ajax-modal", )
    icon = "plus"
    policy_rules = ("network",)
    success_url = SUCCESS_URL


class CreateListenerLink(tables.LinkAction):
    name = "createlistener"
    verbose_name = _("Create Listener")
    url = URL_PREFIX + "createlistener"
    classes = ("ajax-modal", )
    icon = "plus"
    policy_rules = ("network", )
    success_url = SUCCESS_URL


class CreatePoolLink(tables.LinkAction):
    name = "createpool"
    verbose_name = _("Create Pool")
    url = URL_PREFIX + "createpool"
    classes = ("ajax-modal", )
    icon = "plus"
    policy_rules = ("network", )
    success_url = SUCCESS_URL


class CreateMemberLink(tables.LinkAction):
    name = "createmember"
    verbose_name = _("Add Member")
    url = URL_PREFIX + "createmember"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = ("network", )
    success_url = SUCCESS_URL

    def get_link_url(self, datum):
        return reverse_lazy(URL_PREFIX + "createmember", kwargs={'pool_id': datum["id"]})


class CreateHealthMonitorLink(tables.LinkAction):
    name = "createhealthmonitor"
    verbose_name = _("Create Health Monitor")
    url = URL_PREFIX + "createmonitor"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = ("network", )


class CreateCertificateLink(tables.LinkAction):
    name = "createcertificate"
    verbose_name = _("Create Certificate")
    url = URL_PREFIX + "createcertificate"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = ("network", )


class DeleteVipAction(tables.DeleteAction):
    name = "deletevip"
    verbose_name = _("Delete VIP")
    redirect_url = reverse_lazy(URL_PREFIX + "index")
    failure_message = _('Failed to delete VIP')

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete VIP",
            u"Delete VIPs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Scheduled deletion of VIP",
            u"Scheduled deletion of VIPs",
            count
        )

    def allowed(self, request, obj):
        return True


class DeleteLoadBalancerAction(tables.DeleteAction):
    name = "deletelb"
    verbose_name = _("Delete Load Balancer")
    redirect_url = reverse_lazy(URL_PREFIX + "index")
    failure_message = _('Failed to delete Load Balancer')

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Load Balancer",
            u"Delete Load Balancers",
            count)

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Scheduled Deletion of Load Balancer",
            u"Scheduled Deletion of Load Balancers",
            count)

    def allowed(self, request, obj):
        return allow_delete("loadbalancer", obj) if obj else any(
                filter(lambda x: allow_delete("loadbalancer", x.datum),
                   self.table.get_rows()))


class DeleteListenerAction(tables.DeleteAction):
    name = "deletelistener"
    verbose_name = _("Delete Listener")
    redirect_url = reverse_lazy(URL_PREFIX + "index")
    failure_message = _("Failed to delete Listener")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Listener",
            u"Delete Listeners",
            count)

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Scheduled Deletion of Listener",
            u"Scheduled Deletion of Listeners",
            count)

    def allowed(self, request, obj):
        return allow_delete("listener", obj) if obj else any(
                filter(lambda x: allow_delete("listener", x.datum),
                   self.table.get_rows()))


class DeletePoolAction(tables.DeleteAction):
    name = "deletepool"
    verbose_name = _("Delete Pool")
    redirect_url = reverse_lazy(URL_PREFIX + "index")
    failure_message = _("Failed to delete Pool")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Pool",
            u"Delete Pools",
            count)

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Scheduled Deletion of Pool",
            u"Scheduled Deletion of Pools",
            count)

    def allowed(self, request, obj):
        return allow_delete("pool", obj) if obj else any(
                filter(lambda x: allow_delete("pool", x.datum),
                   self.table.get_rows()))

class DeleteMemberAction(tables.DeleteAction):
    name = "deletemember"
    verbose_name = _("Delete Member")
    success_url = reverse_lazy(URL_PREFIX + "index")
    failure_message = _("Failed to delete Member")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Member",
            u"Delete Members",
            count)

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Scheduled Deletion of Member",
            u"Scheduled Deletion of Members",
            count)

    def allowed(self, request, obj):
        return allow_delete("member", obj) if obj else any(
                filter(lambda x: allow_delete("member", x.datum),
                   self.table.get_rows()))


class DeleteHealthMonitorAction(tables.DeleteAction):
    name = "deletehealthmonitor"
    verbose_name = _("Delete Health Monitor")
    redirect_url = reverse_lazy(URL_PREFIX + "index")
    failure_message = _("Failed to delete Health Monitor")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Health Monitor",
            u"Delete Health Monitors",
            count)

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Scheduled Deletion of Health Monitor",
            u"Scheduled Deletion of Health Monitors",
            count)

    def allowed(self, request, obj):
        return allow_delete("healthmonitor", obj) if obj else any(
                filter(lambda x: allow_delete("healthmonitor", x.datum),
                   self.table.get_rows()))


class DeleteCertificateLink(tables.DeleteAction):
    name = "deletecertificate"
    verbose_name = _("Delete Certificate")
    redirect_url = reverse_lazy(URL_PREFIX + "index")
    failure_message = _("Failed to delete Certificate")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Certificate",
            u"Delete Certificates",
            count)

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Scheduled Deletion of Certificate",
            u"Scheduled Deletion of Certificates",
            count)

    def allowed(self, request, obj):
        # check for bindings.
        return True


class MigrateVipAction(tables.LinkAction):
    pass


class TestVipAction(tables.Action):
    name = "testvip"
    verbose_name = _("Test VIP")
    url = URL_PREFIX + "test"
    classes = tuple()
    policy_rules = ("network",)
    success_url = "horizon:project:a10vips:index"
    method = "GET"
    requires_input = True
    enabled = False

    def single(self, data_table, request, object_id):
        # Test methods need to be put into a lib
        # Start low level - ping, tcp, http, https
        return True

    def allowed(self, request, obj):
        # TODO(mdurrant) - We need an extension that performs this action.
        # Put in logic here for whether or not we can actually test something.
        return True


class UpdateLoadBalancerAction(tables.LinkAction):
    name = "editlb"
    verbose_name = _("Edit Load Balancer")
    url = URL_PREFIX + "editlb"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = ("network",)  # FIXME(mdurrant) - A10-specific policies?
    success_url = "horizon:project:a10vips:index"

    def get_link_url(self, datum):
        base_url = reverse(URL_PREFIX + "editlb",
                           kwargs={'id': datum["id"]})
        return base_url


class UpdateListenerAction(tables.LinkAction):
    name = "editlistener"
    verbose_name = _("Edit Listener")
    url = URL_PREFIX + "editlistener"
    classes = ("ajax-modal", )
    icon = "plus"
    policy_rules = ("network", )
    success_url = "horizon:project:a10vips:index"

    def get_link_url(self, datum):
        base_url = reverse(URL_PREFIX + self.name,
                           kwargs={'id': datum["id"]})
        return base_url


class UpdatePoolAction(tables.LinkAction):
    name = "editpool"
    verbose_name = _("Edit Pool")
    url = URL_PREFIX + "editpool"
    classes = ("ajax-modal", )
    icon = "plus"
    policy_rules = ("network", )
    success_url = "horizon:project:a10vips:index"

    def get_link_url(self, datum):
        base_url = reverse(URL_PREFIX + self.name,
                           kwargs={'id': datum["id"]})
        return base_url


class UpdateCertificateAction(tables.LinkAction):
    name = "editcertificate"
    verbose_name = _("Edit Certificate")
    url = URL_PREFIX + "editcertificate"
    classes = ("ajax-modal", )
    icon = "plus"
    policy_rules = ("network", )
    success_url = "horizon:project:a10vips:index"

    def get_link_url(self, datum):
        base_url = reverse(URL_PREFIX + self.name,
                           kwargs={'cert_id': datum["id"]})
        self.submit_url = base_url
        return base_url


class VipTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    name = tables.Column("name", verbose_name=_("Name"), link=links.link_loadbalancer_detail_by_id)
    ip_address = tables.Column("vip_address", verbose_name=_("IP Address"))
    provision_status = tables.Column("provisioning_status",
                                     verbose_name=_("Provisioning Status"))
    provider = tables.Column("provider", verbose_name=_("Provider"))
    op_status = tables.Column("op_status",
                              verbose_name=_("Operating Status"))

    def get_object_id(self, datum):
        return datum.get("id")

    class Meta(object):
        name = "viptable"
        verbose_name = "viptable"
        table_actions = (CreateVipLink, DeleteVipAction,)
        row_actions = (DeleteVipAction, )


class OverviewPoolTable(base.PoolTableBase):

    class Meta(object):
        name = "overviewpooltable"
        verbose_name = "Pool Overview"
        table_actions = tuple()
        row_actions = tuple()


class ProjectHealthMonitorTable(base.HealthMonitorTableBase):

    def set_multiselect_column_visibility(self, visible):
        allowed = any(filter(lambda x: allow_delete("healthmonitor", x.datum), self.get_rows()))
        return super(ProjectHealthMonitorTable, self).set_multiselect_column_visibility(visible=allowed)

    class Meta(object):
        name = "projecthealthmonitortable"
        verbose_name = _("Health Monitors")
        table_actions = (CreateHealthMonitorLink, DeleteHealthMonitorAction, )
        row_actions = (DeleteHealthMonitorAction, )


class ProjectMemberTable(base.MemberTableBase):

    def set_multiselect_column_visibility(self, visible):
        allowed = any(filter(lambda x: allow_delete("member", x.datum), self.get_rows()))
        return super(ProjectMemberTable, self).set_multiselect_column_visibility(visible=allowed)

    class Meta(object):
        name = "projectmembertable"
        verbose_name = _("Member Servers")
        table_actions = (DeleteMemberAction,)
        row_actions = (DeleteMemberAction,)


class ProjectPoolTable(base.PoolTableBase):

    def set_multiselect_column_visibility(self, visible):
        allowed = any(filter(lambda x: allow_delete("pool", x.datum), self.get_rows()))
        return super(ProjectPoolTable, self).set_multiselect_column_visibility(visible=allowed)

    class Meta(object):
        name = "projectpooltable"
        verbose_name = "Pools"
        table_actions = (CreatePoolLink, DeletePoolAction, )
        row_actions = (UpdatePoolAction, DeletePoolAction, CreateMemberLink, )


class ProjectListenerTable(base.ListenerTableBase):

    def set_multiselect_column_visibility(self, visible):
        allowed = any(filter(lambda x: allow_delete("listener", x.datum), self.get_rows()))
        return super(ProjectListenerTable, self).set_multiselect_column_visibility(visible=allowed)

    class Meta(object):
        name = "projectlistenertable"
        verbose_name = "Listeners"
        table_actions = (CreateListenerLink, DeleteListenerAction,)
        row_actions = (UpdateListenerAction, DeleteListenerAction,)


class ProjectLoadbalancerTable(base.LoadbalancerTableBase):

    def set_multiselect_column_visibility(self, visible):
        allowed = any(filter(lambda x: allow_delete("loadbalancer", x.datum), self.get_rows()))
        return super(ProjectLoadbalancerTable, self).set_multiselect_column_visibility(visible=allowed)


    class Meta(object):
        name = "projectloadbalancertable"
        verbose_name = _("Load Balancers")
        table_actions = (CreateLoadBalancerLink, DeleteLoadBalancerAction, )
        row_actions = (UpdateLoadBalancerAction, DeleteLoadBalancerAction, )


class ProjectCertificateTable(base.CertificateTableBase):

    class Meta(object):
        name = "projectcertificatetable"
        verbose_name = _("Certificates")
        table_actions = (CreateCertificateLink, DeleteCertificateLink,)
        row_actions = (UpdateCertificateAction, DeleteCertificateLink, )
