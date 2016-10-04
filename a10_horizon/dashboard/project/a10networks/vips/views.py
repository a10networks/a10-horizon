# Copyright (C) 2016, A10 Networks Inc. All rights reserved.
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
import re

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tables
from horizon import tabs
from horizon import workflows

from horizon.utils import memoized

LOG = logging.getLogger(__name__)


# TODO(mdurrant) move this into a module that exposes lbaasv2 and raises an exception if not
# lbaasv2 api
try:
    from neutron_lbaas_dashboard.api import lbaasv2 as lbaasv2_api
except ImportError as ex:
    LOG.exception(ex)
    LOG.warning("Could not import lbaasv2 dashboard API")

import base_table
import forms as p_forms
import tables as p_tables
import tabs as p_tabs
import workflows as p_workflows

URL_PREFIX = "horizon:project:a10vips:"
SUCCESS_URL = URL_PREFIX + "index"

ACTION = "action"
NOUN = "noun"
PLURAL = "plural"


class IndexView(tabs.TabView):
    template_name = "vips/vip_tabs.html"
    tab_group_class = p_tabs.A10LBTabs
    page_title = "Load Balancers"

    # TODO(mdurrant) - Move this to a helper method. If exceptions are raised,
    # return a list of errors to be bubbled to the UI.
    def _lb_delete_nested(request, lb_id):
        lb_details = lbaasv2_api.get_loadbalancer(request, lb_id)

        errors = []

        for listener in lb_details.get("listeners"):
            listener_id = listener.get("id")
            try:
                lbaasv2_api.delete_listener(request, listener_id)
            except Exception as e:
                # We can't continue with things we can't delete.
                LOG.exception(e)
                errors.append("Could not delete listener {0}".format(listener_id))
                break

        if len(errors) < 1:
            try:
                lbaasv2_api.loadbalancer_delete(request, lb_id)
            except Exception as e:
                LOG.exception(e)
                errors.append("Could not delete load balancer {0}")
        else:
            joined = "\n".join(errors)
            exceptions.handle(_(joined))

        return len(errors) < 1

    delete_actions = {
        "vip": {
            ACTION: _lb_delete_nested,
            NOUN: "VIP",
            PLURAL: "VIPs",
        },
        "listener": {
            ACTION: lbaasv2_api.delete_listener,
            NOUN: "Listener",
            PLURAL: "Listeners"
        },
        "lb": {
            ACTION: lbaasv2_api.loadbalancer_delete,
            NOUN: "Load Balancer",
            PLURAL: "Load Balancers"
        },
        "pool": {
            ACTION: lbaasv2_api.pool_delete,
            NOUN: "Pool",
            PLURAL: "Pools",
        },
        "member": {
            ACTION: lbaasv2_api.member_delete,
            NOUN: "Member",
            PLURAL: "Members",
        },
        "healthmonitor": {
            ACTION: lbaasv2_api.healthmonitor_delete,
            NOUN: "Health Monitor",
            PLURAL: "Health Monitors"
        }
    }

    def post(self, request, *args, **kwargs):
        obj_ids = request.POST.getlist('object_ids')
        action = request.POST['action']
        m = re.search('.delete([a-z]+)', action).group(1)

        if obj_ids == []:
            obj_ids.append(re.search('([0-9a-z-]+)$', action).group(1))

        if m in self.delete_actions:
            delete_action = self.delete_actions[m]
            for obj_id in obj_ids:
                success_msg = "Deleted {0} {1}".format(delete_action[NOUN], obj_id)
                failure_msg = "Unable to delete {0} {1}".format(delete_action[NOUN], obj_id)

                try:
                    delete_action[ACTION](request, obj_id)
                    messages.success(request, success_msg)
                except Exception as ex:
                    exceptions.handle(request, failure_msg)
                    LOG.exception(ex)

        return self.get(request, *args, **kwargs)


class UpdateLoadBalancerView(forms.views.ModalFormView):
    name = _("Update Load Balancer")
    form_class = p_forms.UpdateLoadBalancerForm
    context_object_name = "loadbalancer"
    success_url = reverse_lazy(SUCCESS_URL)
    template_name = "lb/update.html"
    page_title = name

    def get_context_data(self, **kwargs):
        context = super(UpdateLoadBalancerView, self).get_context_data(**kwargs)
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        id = self.kwargs['id']
        self.submit_url = reverse_lazy(URL_PREFIX + "edit",
                                       kwargs={"id": id})
        if id:
            try:
                return lbaasv2_api.get_loadbalancer(self.request, id)
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve Load Balancer: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        rv = self._get_object()
        return rv


class UpdateListenerView(forms.views.ModalFormView):
    name = _("Update Listener")
    form_class = p_forms.UpdateListenerForm
    context_object_name = "listener"
    success_url = reverse_lazy(SUCCESS_URL)
    template_name = "lb/listeners/update.html"
    page_title = name

    def get_context_data(self, **kwargs):
        context = super(UpdateListenerView, self).get_context_data(**kwargs)
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        id = self.kwargs['id']
        self.submit_url = reverse_lazy(URL_PREFIX + "editlistener",
                                       kwargs={"id": id})
        if id:
            try:
                return lbaasv2_api.show_listener(self.request, id)
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve VIP: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        rv = self._get_object()
        return rv


class UpdatePoolView(forms.views.ModalFormView):
    name = _("Update Pool")
    form_class = p_forms.UpdatePoolForm
    context_object_name = "pool"
    success_url = reverse_lazy(SUCCESS_URL)
    template_name = "lb/pools/update.html"
    page_title = name

    def get_context_data(self, **kwargs):
        context = super(UpdatePoolView, self).get_context_data(**kwargs)
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        id = self.kwargs['id']
        self.submit_url = reverse_lazy(URL_PREFIX + "editpool",
                                       kwargs={"id": id})
        if id:
            try:
                return lbaasv2_api.pool_get(self.request, id)
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve Pool: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        rv = self._get_object()
        if rv is not None:
            rv = self.flatten(rv)
        return rv

    def flatten(self, obj):
        sp = obj.get("session_persistence") or {}

        return {
            "id": obj.get("id"),
            "name": obj.get("name"),
            "description": obj.get("description"),
            "lb_algorithm": obj.get("lb_algorithm"),
            "session_persistence": sp.get("type", "").lower(),
            "cookie_name": sp.get("cookie_name", ""),
        }


class UpdateMemberView(forms.views.ModalFormView):
    name = _("Member Pool")
    form_class = p_forms.UpdateMemberForm
    context_object_name = "member"
    success_url = reverse_lazy(SUCCESS_URL)
    template_name = "lb/members/update.html"
    page_title = name

    def get_context_data(self, **kwargs):
        context = super(UpdatePoolView, self).get_context_data(**kwargs)
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        id = self.kwargs['id']
        self.submit_url = reverse_lazy(URL_PREFIX + "editmember",
                                       kwargs={"id": id})
        if id:
            try:
                return lbaasv2_api.member_get(self.request, id)
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve Pool: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        rv = self._get_object()
        if rv is not None:
            rv = self.flatten(rv)
        return rv

    def flatten(self, obj):
        sp = obj.get("session_persistence") or {}

        return {
            "id": obj.get("id"),
            "name": obj.get("name"),
            "description": obj.get("description"),
            "lb_algorithm": obj.get("lb_algorithm"),
            "session_persistence": sp.get("type", "").lower(),
            "cookie_name": sp.get("cookie_name", ""),
        }


class CreateVipView(workflows.WorkflowView):
    name = _("Create VIP")
    workflow_class = p_workflows.CreateVipWorkflow
    success_url = reverse_lazy(SUCCESS_URL)


class CreateLoadBalancerView(workflows.WorkflowView):
    name = _("Create Load Balancer")
    workflow_class = p_workflows.CreateLoadBalancerWorkflow
    success_url = reverse_lazy(SUCCESS_URL)


class CreateListenerView(workflows.WorkflowView):
    name = _("Create Listener")
    workflow_class = p_workflows.CreateListenerWorkflow
    success_url = reverse_lazy(SUCCESS_URL)


class CreatePoolView(workflows.WorkflowView):
    name = _("Create Pool")
    workflow_class = p_workflows.CreatePoolWorkflow
    success_url = reverse_lazy(SUCCESS_URL)


class CreateMemberView(workflows.WorkflowView):
    name = _("Create Member")
    workflow_class = p_workflows.CreateMemberWorkflow
    success_url = reverse_lazy(SUCCESS_URL)
    template_name = "lb/members/create.html"

    def get_context_data(self, **kwargs):
        return super(CreateMemberView, self).get_context_data(**kwargs)

    def get_initial(self):
        self.submit_url = reverse_lazy(URL_PREFIX + "createmember",
                                       kwargs=self.kwargs)
        return self.kwargs


class CreateMonitorView(workflows.WorkflowView):
    name = _("Create Health Monitor")
    workflow_class = p_workflows.CreateHealthMonitorWorkflow
    success_url = reverse_lazy(SUCCESS_URL)


class ListenerTableDataSourceMixin(object):

    def get_listenertable_data(self):
        rv = []
        try:
            initial = self.get_initial()
            listener_ids = initial.get("listeners", []) or []
            if len(listener_ids) > 0:
                listeners = map(lambda x: lbaasv2_api.show_listener(self.request, x.get("id")),
                                listener_ids)
                rv = listeners
            return rv
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(self.request,
                              _('Unable to retrieve parent listeners list.'))
        return rv


class MonitorDetailView(tables.MultiTableView):
    name = _("Monitor Details")
    context_object_name = "healthmonitor"
    success_url = reverse_lazy(URL_PREFIX + "index")
    template_name = "lb/monitors/detail.html"
    page_title = name
    tab_group_class = p_tabs.MonitorDetailsTabs
    table_classes = (base_table.PoolTableBase,)

    def get_context_data(self, **kwargs):
        context = super(MonitorDetailView, self).get_context_data(**kwargs)
        context[self.context_object_name] = self.get_initial()
        context["pool"] = self._get_pool()
        return context

    # Get the pool IDs from the initial object and fetch their details
    def get_pooltable_data(self):
        rv = []
        monitor = self.get_initial()
        pool_ids = map(lambda x: x.get("id"), monitor.get("pools"))

        try:
            for p in pool_ids:
                # map fails here for bizarre reasons.
                pool = lbaasv2_api.pool_get(self.request, p)
                rv.append(pool)
            return rv
        except Exception as ex:

            LOG.exception(ex)
            exceptions.handle(self.request,
                              _('Unable to retrieve associated Pools list.'))
            return []

    @memoized.memoized_method
    def _get_pool(self):
        rv = {}

        pool_id = None
        # pool_id = self.context[self.context_object_name].get("pool_id")
        if pool_id:
            try:
                rv = lbaasv2_api.pool_get(self.request, pool_id)
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve Pool: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)
                LOG.exception(ex)
        return rv

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        rv = {}
        id = self.kwargs['id']

        self.submit_url = reverse_lazy(URL_PREFIX + "editmonitor",
                                       kwargs={"id": id})
        if id:
            try:
                rv = lbaasv2_api.healthmonitor_get(self.request, id).get(self.context_object_name)
                return rv
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve Member: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        rv = self._get_object()
        return rv


class MemberDetailView(tabs.TabView):
    name = _("Member Details")
    context_object_name = "member"
    success_url = reverse_lazy(URL_PREFIX + "index")
    template_name = "lb/members/detail.html"
    page_title = name
    tab_group_class = p_tabs.MemberDetailsTabs

    def get_context_data(self, **kwargs):
        context = super(MemberDetailView, self).get_context_data(**kwargs)
        context[self.context_object_name] = self.get_initial()
        context["pool"] = self._get_pool()
        return context

    @memoized.memoized_method
    def _get_pool(self):
        rv = {}
        pool_id = self.kwargs["pool_id"]

        if pool_id:
            try:
                rv = lbaasv2_api.pool_get(self.request, pool_id)
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve pool: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)
                LOG.exception(ex)
        return rv

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        rv = {}
        id = self.kwargs['id']
        pool_id = self.kwargs['pool_id']

        self.submit_url = reverse_lazy(URL_PREFIX + "editmember",
                                       kwargs={"id": id})
        if id:
            try:
                rv = lbaasv2_api.member_get(self.request, id, pool_id)
                return rv
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve Member: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        rv = self._get_object()
        return rv


class PoolDetailView(tables.MultiTableView, ListenerTableDataSourceMixin):
    name = _("Pool Details")
    context_object_name = "pool"
    success_url = reverse_lazy(URL_PREFIX + "index")
    template_name = "lb/pools/detail.html"
    page_title = name
    tab_group_class = p_tabs.PoolDetailsTabs
    table_classes = (p_tables.ProjectMemberTable, base_table.ListenerTableBase,)

    def get_context_data(self, **kwargs):
        context = super(PoolDetailView, self).get_context_data(**kwargs)
        context[self.context_object_name] = self.get_initial()
        context["pool_id"] = context[self.context_object_name].get("id")
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        rv = {}
        id = self.kwargs['id']
        self.submit_url = reverse_lazy(URL_PREFIX + "edit",
                                       kwargs={"id": id})
        if id:
            try:
                rv = lbaasv2_api.pool_get(self.request, id)
                return rv
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve Pool: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        return self._get_object()

    # We only get one pool - but table displays are easy on the eyes.
    def get_projectmembertable_data(self):
        rv = []
        try:
            pool_id = self.kwargs['id']
            pool = self.get_initial()
            members = pool.get("members", []) or []
            member_ids = map(lambda x: str(x.get("id")), members)

            if len(member_ids) > 0:
                members = map(lambda x: lbaasv2_api.member_get(self.request, x, pool_id),
                              member_ids)
                # members = map(lambda x: self.set_pool_on_member(x, pool_id), members)
                rv = members
            return rv
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(self.request,
                              _('Unable to retrieve member list.'))
        return rv


class ListenerDetailView(tables.MultiTableView):
    name = _("Listener Details")
    context_object_name = "listener"
    success_url = reverse_lazy(URL_PREFIX + "index")
    page_title = "Listener {{ listener.name }} - Details"
    template_name = "lb/listeners/detail.html"
    table_classes = (base_table.PoolTableBase, base_table.LoadbalancerTableBase,)
    tab_group_class = p_tabs.ListenerDetailsTabs

    def get_context_data(self, **kwargs):
        context = super(ListenerDetailView, self).get_context_data(**kwargs)
        context[self.context_object_name] = self.get_initial()
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):

        id = self.kwargs['id']
        if id:
            try:
                rv = lbaasv2_api.show_listener(self.request, id)
                return rv
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve pool: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        rv = self._get_object()
        return rv

    # We only get one pool - but table displays are easy on the eyes.
    def get_pooltable_data(self):
        rv = []
        try:
            listener = self.get_initial()
            pool_id = listener.get("default_pool_id") or None

            default_pool = {}

            if pool_id is not None:
                default_pool = lbaasv2_api.pool_get(self.request, pool_id)
                if default_pool is not None:
                    rv.append(default_pool)

        except Exception as ex:

            LOG.exception(ex)
            exceptions.handle(self.request,
                              _('Unable to retrieve default pool list.'))
        return rv

    # We only get one pool - but table displays are easy on the eyes.
    def get_loadbalancertable_data(self):
        rv = []
        try:
            listener = self.get_initial()
            lb_ids = listener.get("loadbalancers")

            loadbalancers = map(lambda x: lbaasv2_api.get_loadbalancer(self.request, x.get("id")),
                                lb_ids)

            rv = loadbalancers
        except Exception as ex:

            LOG.exception(ex)
            exceptions.handle(self.request,
                              _('Unable to retrieve loadbalancers list.'))
        return rv


class LBDetailView(tables.MultiTableView, ListenerTableDataSourceMixin):
    name = _("Load Balancer Details")
    context_object_name = "loadbalancer"
    page_title = "Load Balancer {{ loadbalancer.name }}"
    success_url = reverse_lazy(URL_PREFIX + "index")
    template_name = "lb/detail.html"
    table_classes = (base_table.ListenerTableBase,)
    tab_group_class = "a10lbdetailstabs"

    def get_context_data(self, **kwargs):
        context = super(LBDetailView, self).get_context_data(**kwargs)
        context[self.context_object_name] = self.get_initial()
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):

        id = self.kwargs['id']
        if id:
            try:
                rv = lbaasv2_api.get_loadbalancer(self.request, id)
                LOG.info(rv)
                return rv
            except Exception as ex:
                redirect = self.success_url
                msg = _("Unable to retrieve VIP: %s") % ex
                exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        return self._get_object()
