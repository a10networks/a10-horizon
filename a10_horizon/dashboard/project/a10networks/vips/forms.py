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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

LOG = logging.getLogger(__name__)

# from openstack_dashboard import api
# lbaasv2 api

from a10_horizon.dashboard.api import lbaasv2 as lbaasv2_api
from a10_horizon.dashboard.api import certificates as certs_api

from a10_horizon.dashboard.helpers import context_processors as from_ctx
from a10_horizon.dashboard.helpers import ui_helpers as ui_helpers
import api_helpers


LOG = logging.getLogger(__name__)


class UpdateLoadBalancerForm(forms.SelfHandlingForm):

    def __init__(self, *args, **kwargs):
        super(UpdateLoadBalancerForm, self).__init__(*args, **kwargs)
        self.submit_url = kwargs.get("id")

    id = forms.CharField(label=_("ID"), widget=forms.TextInput(attrs=ui_helpers.readonly()))
    name = forms.CharField(label=_("Name"), min_length=1, max_length=255,
                           required=True)
    description = forms.CharField(label=_("Description"), min_length=1,
                                  max_length=255, required=False)

    failure_url = "horizon:project:a10vips:index"
    success_url = "horizon:project:a10vips:index"

    def handle(self, request, context):
        try:
            lb_id = context.get("id")
            del context["id"]
            body = {"loadbalancer": context}
            lb = lbaasv2_api.update_loadbalancer(request, lb_id, **body)
            msg = _("Load Balancer {0} was successfully updated").format(context["name"])
            messages.success(request, msg)
            return lb
        except Exception as ex:
            msg = _("Failed to update VIP %s") % context["name"]
            LOG.exception(ex)
            redirect = reverse_lazy(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)


class UpdateListenerForm(forms.SelfHandlingForm):

    def __init__(self, *args, **kwargs):
        super(UpdateListenerForm, self).__init__(*args, **kwargs)
        self.submit_url = kwargs.get("id")

    id = forms.CharField(label=_("ID"), widget=forms.TextInput(attrs=ui_helpers.readonly()))
    name = forms.CharField(label=_("Name"), min_length=1, max_length=255,
                           required=True)
    description = forms.CharField(label=_("Description"), min_length=1,
                                  max_length=255, required=False)
    connection_limit = forms.IntegerField(label=_("Connection Limit"))

    failure_url = "horizon:project:a10vips:index"
    success_url = "horizon:project:a10vips:index"

    def handle(self, request, context):
        try:
            listener_id = context.get("id")
            del context["id"]
            body = {"listener": context}
            lb = lbaasv2_api.update_listener(request, listener_id, **body)
            msg = _("Listener {0} was successfully updated").format(context["name"])
            messages.success(request, msg)
            return lb
        except Exception as ex:
            msg = _("Failed to update Listener %s") % context["name"]
            LOG.exception(ex)
            redirect = reverse_lazy(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)


class UpdatePoolForm(forms.SelfHandlingForm):
    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput(attrs=ui_helpers.readonly()))
    name = forms.CharField(label=_("Name"), min_length=1, max_length=255,
                           required=True)
    description = forms.CharField(label=_("Description"), min_length=1,
                                  max_length=255, required=False)
    lb_algorithm = forms.ChoiceField(label=_("LB Algorithm"), required=True)
    session_persistence = forms.ChoiceField(label=_("Session Persistence"),
                                            widget=forms.Select(
                                            attrs={
                                                "class": "switchable",
                                                "data-slug": "session_persistence"
                                            }),
                                            required=True)
    cookie_name = forms.CharField(label=_("Cookie Name"), min_length=1, max_length=255,
                                  widget=forms.TextInput(
                                  attrs={
                                      "class": "switched",
                                      "data-switch-on": "session_persistence",
                                      "data-session_persistence-app_cookie": _("App Cookie Name")
                                  }),
                                  required=False)
    admin_state_up = forms.BooleanField(label=_("Admin State"), required=False, initial=True)

    failure_url = "horizon:project:a10vips:index"
    success_url = "horizon:project:a10vips:index"

    def __init__(self, request, *args, **kwargs):
        initial = kwargs.get("initial", {})
        sp_type = ""
        sp_cookie = ""

        if initial is not None:
            sp_type = initial.get("session_persistence", "")
            sp_cookie = initial.get("cookie_name", "")

        super(UpdatePoolForm, self).__init__(request, *args, **kwargs)

        self.fields["session_persistence"].choices = api_helpers.session_persistence_field_data(
            request, True)
        self.fields["lb_algorithm"].choices = api_helpers.lb_algorithm_field_data(request, False)

        self.fields["session_persistence"].initial = sp_type.lower()
        self.fields["cookie_name"].initial = sp_cookie

        self.submit_url = kwargs.get("id")

    def handle(self, request, context):
        try:
            pool_id = context.get("id")
            del context["id"]
            body = self.body_from_context(context)
            lb = lbaasv2_api.pool_update(request, pool_id, **body)
            msg = _("Pool {0} was successfully updated").format(context["name"])
            messages.success(request, msg)
            return lb
        except Exception as ex:
            msg = _("Failed to update Pool %s") % context["name"]
            LOG.exception(ex)
            redirect = reverse_lazy(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)

    def body_from_context(self, context):
        rv = {"pool": {
            "name": context.get("name"),
            "description": context.get("description"),
            "lb_algorithm": context.get("lb_algorithm"),
            "admin_state_up": context.get("admin_state_up")
        }}
        from_ctx.populate_session_persistence_from_context(context, rv)
        return rv


class UpdateMemberForm(forms.SelfHandlingForm):
    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput(ui_helpers.readonly()))
    pool_id = forms.CharField(label=_("ID"),
                              widget=forms.HiddenInput(attrs=ui_helpers.readonly()))
    weight = forms.IntegerField(label=_("Weight"))
    admin_state_up = forms.BooleanField(label=_("Admin State"), required=False, initial=True)

    failure_url = "horizon:project:a10vips:index"
    success_url = "horizon:project:a10vips:index"

    def __init__(self, request, *args, **kwargs):
        super(UpdateMemberForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, context):
        try:
            pool_id = context["pool"]
            del context["id"]
            del context["pool_id"]

            body = self.body_from_context(context)
            member = lbaasv2_api.member_update(request, pool_id, **body)
            msg = _("Member {0} was successfully updated").format(context["name"])
            messages.success(request, msg)
            return member
        except Exception as ex:
            msg = _("Failed to update Member %s") % context["name"]
            LOG.exception(ex)
            redirect = reverse_lazy(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)

    def body_from_context(self, context):
        return {"member": {
            "name": context.get("name"),
            "weight": context.get("weight")}}


class UpdateCertificateForm(forms.SelfHandlingForm):
    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput(
        attrs=ui_helpers.readonly()), required=True)
    name = forms.CharField(label=_("Name"), min_length=1, max_length=255,
                           required=True)
    # description = forms.CharField(label=_("Description"), min_length=1,
    #                               max_length=255, required=False)
    cert_data = forms.CharField(widget=forms.HiddenInput(
        attrs=ui_helpers.readonly()), required=True)
    key_data = forms.CharField(widget=forms.HiddenInput(
        attrs=ui_helpers.readonly()), required=True)
    intermediate_data = forms.CharField(widget=forms.HiddenInput(
        attrs=ui_helpers.readonly()), required=True)
    password = forms.CharField(widget=forms.HiddenInput(
        attrs=ui_helpers.readonly()), required=True)

    failure_url = "horizon:project:a10vips:index"
    success_url = "horizon:project:a10vips:index"

    def __init__(self, *args, **kwargs):
        super(UpdateCertificateForm, self).__init__(*args, **kwargs)
        initial = kwargs.get("initial", {})

        if initial is not None:
            kwid = initial.get("id")
            self.submit_url = kwid

    def handle(self, request, context):
        try:
            body = self.body_from_context(context)
            id = context["id"]
            self.kwargs["id"] = id
            cert = certs_api.update_certificate(**body)
            msg = _("Certificate {0} was successfully updated").format(context["name"])
            messages.success(request, msg)
            return cert
        except Exception as ex:
            msg = _("Failed to update Certificate %s") % context["name"]
            LOG.exception(ex)
            redirect = reverse_lazy(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)

    def body_from_context(self, context):
        return {"a10_certificate": {
            "name": str(context.get("name")),
            "description": str(context.get("description")),
            "cert_data": context.get("cert_data"),
            "key_data": context.get("key_data"),
            "id": context.get("id")
        }}
