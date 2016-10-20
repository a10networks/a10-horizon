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

from horizon import conf as horizon_conf
from horizon import exceptions
from horizon import forms
from horizon import workflows


# Yeah, instances in networking - easy way to get subnet data.
from openstack_dashboard.dashboards.project.instances import utils as instance_utils
from openstack_dashboard.utils import settings as settings_utils

from a10_horizon.dashboard.api import certificates
from a10_horizon.dashboard.api import lbaasv2
from a10_horizon.dashboard.helpers import context_processors as from_ctx

import api_helpers
from a10_horizon.dashboard.helpers import ui_helpers


LOG = logging.getLogger(__name__)

"""
Notes:

v2 defines a VIP as a combination of a listener/loadbalancer.

"""

"""
Constants because no one likes magic numbers.
"""
URL_PREFIX = "horizon:project:a10vips:"
SUCCESS_URL = URL_PREFIX + "index"

LISTENER_POOL_PROTOCOLS = {
    # listenerProtocol: [validPoolProtocol ]
    "HTTP": ["HTTP", "HTTPS"],
    "HTTPS": ["HTTPS"],
    "TCP": ["HTTP", "HTTPS", "TCP"]
}


class CreateLbAction(workflows.Action):
    lb_name = forms.CharField(label=_("Name"), min_length=1, max_length=255, required=True)
    lb_description = forms.CharField(label=_("Description"), min_length=1, max_length=255,
                                     required=False)
    vip_subnet = forms.ChoiceField(label=_("VIP Subnet"), required=True)
    admin_state_up = forms.BooleanField(label=_("Admin State"), required=False, initial=True)

    def populate_vip_subnet_choices(self, request, context):
        return api_helpers.subnet_field_data(request)

    class Meta(object):
        name = _("LB Name and Subnet")
        # TODO(mdurrant) - Add a10-specific permissions
        permissions = ("openstack.services.network", )
        help_text = _("Specify the details for the Load Balancer below")


class CreateListenerAction(workflows.Action):
    loadbalancer_id = forms.ChoiceField(label=_("Load Balancer"), required=True)
    listener_name = forms.CharField(label=_("Name"),
                                    min_length=1, max_length=255,
                                    required=True)
    listener_description = forms.CharField(label=_("Description"), min_length=1, max_length=255,
                                           required=False)
    protocol = forms.ChoiceField(label=_("Protocol"), required=True)
    protocol_port = forms.IntegerField(label=_("Protocol Port"),
                                       min_value=1, max_value=65535,
                                       required=True)
    # TODO(mdurrant): Add connection limit
    connection_limit = forms.IntegerField(
        label=_("Connection Limit"), min_value=-1, max_value=65535, initial=-1)

    def populate_loadbalancer_id_choices(self, request, context):
        return api_helpers.loadbalancer_field_data(request)

    def populate_protocol_choices(self, request, context):
        # TODO(mdurrant) - Return these from a service
        return api_helpers.listener_protocol_field_data(request)

    class Meta(object):
        name = _("Listener Data")
        # TODO(mdurrant) - Add a10-specific permissions
        permissions = ("openstack.services.network", )
        help_text = _("Specify the details for the listener protcol and port below")


class CreatePoolAction(workflows.Action):
    pool_name = forms.CharField(label=_("Name"), required=True)
    description = forms.CharField(label=_("Description"), required=False)
    listener_id = forms.ChoiceField(label=_("Listener"), required=True)
    lb_algorithm = forms.ChoiceField(label=_("LB Algorithm"), required=True)
    pool_protocol = forms.ChoiceField(label=_("Pool Protocol"), required=True)

    def populate_listener_id_choices(self, request, context):
        return api_helpers.listener_field_data(request)

    def populate_lb_algorithm_choices(self, request, context):
        # These are the openstack defaults.
        # We'll be getting these from our own web service soon.
        return api_helpers.lb_algorithm_field_data(request)

    def populate_pool_protocol_choices(self, request, context):
        return api_helpers.pool_protocol_field_data(request)

    class Meta(object):
        name = _("Create Pool")
        # TODO(mdurrant) - Add a10-specific permissions
        permissions = ("openstack.services.network", )
        help_text = _("Specify name, algorithm, and session persistence for pool")


class CreateMemberAction(workflows.Action):
    pool_id = forms.Field(widget=forms.HiddenInput, initial="")
    name = forms.CharField(label=_("Name"))
    weight = forms.IntegerField(label=_("Weight"), min_value=1, max_value=65535,
                                required=True)
    member_subnet_id = forms.ChoiceField(label=_("Member Subnet"), required=True)
    # TODO(mdurrant) - Make a checkbox setting DHCP/manual
    member_address = forms.GenericIPAddressField(label=_("Member IP"), required=False)
    member_protocol_port = forms.IntegerField(label=_("Protocol Port"), min_value=1,
                                              max_value=65535, required=True)
    admin_state_up = forms.BooleanField(label=_("Admin State"), required=False, initial=True)

    def __init__(self, request, *args, **kwargs):
        super(CreateMemberAction, self).__init__(request, *args, **kwargs)
        # TODO(mdurrant) Get this of this nonsense.
        if len(args) > 0:
            pool_id = args[0].get("pool_id")
            self.detail_url = URL_PREFIX + "createmember"
            self.success_url = reverse_lazy(self.detail_url, kwargs={"pool_id": pool_id})

    def populate_member_subnet_id_choices(self, request, context):
        return api_helpers.subnet_field_data(request)

    def populate_pool_id_choices(self, request, context):
        return api_helpers.pool_field_data(request)

    class Meta(object):
        name = _("Create Member")
        # TODO(mdurrant) - Add a10-specific permissions
        permissions = ("openstack.services.network", )
        help_text = _("Specify pool, weight, subnet/address, and port for member.")


class CreateHealthMonitorAction(workflows.Action):

    def __init__(self, request, *args, **kwargs):
        super(CreateHealthMonitorAction, self).__init__(request, *args, **kwargs)
        if len(args) > 0:
            self.detail_url = URL_PREFIX + "createmonitor"
            self.success_url = reverse_lazy(self.detail_url)

    def hide_http(title):
        return ui_helpers.switched_field("monitor_type", ({"http": title, "https": title}))

    pool_id = forms.ChoiceField(label=_("Pool"), required=True)
    monitor_type = forms.ChoiceField(label=_("Monitor Type"), required=True,
                                     widget=forms.Select(
                                     attrs=ui_helpers.switchable_field("monitor_typr")))

    delay = forms.IntegerField(label=_("Delay"), required=True)
    timeout = forms.IntegerField(label=_("Timeout"), required=True)
    max_retries = forms.IntegerField(label=_("Maximum Retries"), required=True)
    http_method = forms.ChoiceField(label=_("HTTP Method"), required=False,
                                    widget=forms.Select(attrs=hide_http("HTTP Method")))
    url_path = forms.CharField(label=_("URL Path"), required=False,
                               widget=forms.TextInput(attrs=hide_http("URL Path")),)
    expected_codes = forms.CharField(label=_("Expected Codes"),
                                     widget=forms.TextInput(attrs=hide_http("Expected Codes")),
                                     required=False, initial="200",
                                     help_text="Expected HTTP codes in comma-separated format.")
    admin_state_up = forms.BooleanField(label=_("Admin State"), required=False, initial=True)

    def populate_pool_id_choices(self, request, context):
        pfilter = lambda x: x.get("healthmonitor_id") is None
        return api_helpers.pool_field_data(request, pfilter)

    def populate_monitor_type_choices(self, request, context):
        return api_helpers.healthmonitor_type_field_data(request)

    def populate_http_method_choices(self, request, context):
        return api_helpers.healthmonitor_httpmethod_field_data(request)

    class Meta(object):
        name = _("Create Health Monitor")
        # TODO(mdurrant) - Add a10-specific permissions
        permissions = ("openstack.services.network", )
        help_text = _("Specify the details for health monitor.")


class CreateCertificateAction(workflows.Action):

    def __init__(self, request, context, *args, **kwargs):
        super(CreateCertificateAction, self).__init__(request, context, *args, **kwargs)
        self._populate_debug_defaults()

    def _random_name(self):
        import random
        chars = []
        for n in range(1, 16):
            chars.append(chr(random.randint(65, 90)))
        return "".join(chars)

    def _populate_debug_defaults(self):
        dev_debug = horizon_conf.HORIZON_CONFIG.get("debug")

        from a10_horizon.tests import testdata

        if dev_debug:
            self.fields["cert_name"].initial = testdata._random_name()
            self.fields["cert_data"].initial = testdata.CERT_DATA
            self.fields["key_data"].initial = testdata.KEY_DATA
            self.fields["password"].initial = ""

    """
        Specify an existing certificate or create a new one.
    """
    # TODO(mdurrant) Create a validator for cert data using cryptography lib
    cert_name = forms.CharField(label=_("Name"),
                                help_text="Specify a name for the certificate data",
                                widget=forms.Textarea(attrs=ui_helpers.textarea_size(rows=1)))
    cert_data = forms.CharField(label=_("Certificate Data"), required=False,
                                widget=forms.Textarea(
                                    attrs=ui_helpers.textarea_size()),
                                min_length=1, max_length=8000)
    description = forms.CharField(label=_("Description"), required=False,
                                  widget=forms.Textarea(attrs=ui_helpers.textarea_size(rows=1)))
    key_data = forms.CharField(label=_("Key Data"), required=False,
                               widget=forms.Textarea(attrs=ui_helpers.textarea_size()),
                               min_length=1, max_length=8000)
    intermediate_data = forms.CharField(label=_("Intermediate Data"), required=False,
                                        widget=forms.Textarea(
                                            attrs=ui_helpers.textarea_size()),
                                        min_length=1, max_length=8000)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)

    class Meta(object):
        name = _("TLS/SSL Certificate Data")
        # TODO(mdurrant) = Add certificate-specific permissions.
        # Delineation of who can/cannot manage certs is critical due to
        # the sensitive nature of the data
        permissions = ("openstack.services.network", )
        help_text = _(
            "Specify data for the new certificate..")


class SpecifyCertificateAction(workflows.Action):

    """
        Specify an existing certificate or create a new one.
    """

    def _populate_debug_defaults(self):
        dev_debug = horizon_conf.HORIZON_CONFIG.get("debug")

        from a10_horizon.tests import testdata

        if dev_debug:
            self.fields["cert_name"].initial = testdata._random_name()
            self.fields["cert_data"].initial = testdata.CERT_DATA
            self.fields["key_data"].initial = testdata.KEY_DATA
            self.fields["password"].initial = ""

    def hide_create_controls(title, merge_attrs={}):
        """
            Returns attributes necessary for hiding/showing
            certificate controls dependent on the choice selected.
        """
        rv = merge_attrs

        rv.update({
            "class": "switched",
            "data-switch-on": "certificate_id",
            "data-certificate_id-_create": title,
        })

        return rv

    # Boolean fields have to be required False else form does not submit.
    use_tls = forms.BooleanField(label=_("Use SSL"), initial=False, required=False)
    certificate_id = forms.ChoiceField(label=_("Select an existing certificate"),
                                       widget=forms.Select(
        attrs=ui_helpers.switchable_field("certificate_id")))

    cert_name = forms.CharField(label=_("Name"),
                                help_text="Specify a name for the certificate data",
                                widget=forms.Textarea(attrs=hide_create_controls(
                                    "Name", ui_helpers.textarea_size(rows=1))))
    description = forms.CharField(label=_("Description"), required=False,
                                  widget=forms.Textarea(attrs=hide_create_controls(
                                      "Description", ui_helpers.textarea_size(rows=1))))
    cert_data = forms.CharField(label=_("Certificate Data"), required=False,
                                widget=forms.Textarea(
                                    attrs=hide_create_controls(
                                        "Certificate Data", ui_helpers.textarea_size())),
                                min_length=1, max_length=8000)
    key_data = forms.CharField(label=_("Key Data"), required=False,
                               widget=forms.Textarea(attrs=hide_create_controls(
                                   "Private Key", ui_helpers.textarea_size())),
                               min_length=1, max_length=8000)
    intermediate_data = forms.CharField(label=_("Intermediate Data"), required=False,
                                        widget=forms.Textarea(
                                            attrs=hide_create_controls(
                                                "Intermediate Data", ui_helpers.textarea_size())),
                                        min_length=1, max_length=8000)
    password = forms.CharField(widget=forms.PasswordInput(
        render_value=False, attrs=hide_create_controls(
            "Password", ui_helpers.textarea_size(rows=1))),
        required=False)

    def __init__(self, request, context, *args, **kwargs):
        super(SpecifyCertificateAction, self).__init__(request, context, *args, **kwargs)
        self._set_control_attributes()
        self._populate_debug_defaults()

    def _set_control_attributes(self):
        # name: title
        controls = {
            "cert_name": "Name",
            "cert_data": "Certificate Data",
            "key_data": "Key Data",
            "intermediate_data": "Intermediate Data",
            "password": "Password"
        }

        for k, v in controls.iteritems():
            f = self.fields.get(k)
            f.label = _(k)

    def populate_certificate_id_choices(self, request, context):
        return api_helpers.certificate_field_data(request)

    class Meta(object):
        name = _("TLS/SSL Certificate Data")
        # TODO(mdurrant) = Add certificate-specific permissions.
        # Delineation of who can/cannot manage certs is critical due to
        # the sensitive nature of the data
        permissions = ("openstack.services.network", )
        help_text = _(
            "Choose an existing certificate or specify certificate data for this listener.")


class CreateVipAction(workflows.Action):
    protocol = forms.ChoiceField(label=_("Protocol"), required=True)
    protocol_port = forms.IntegerField(label=_("Protocol Port"), min_value=1, max_value=65535,
                                       required=True)
    # TODO(mdurrant): Add connection limit

    def populate_vip_subnet_choices(self, request, context):
        return instance_utils.subnet_field_data(request, True)

    def populate_protocol_choices(self, request, context):
        # TODO(mdurrant) - Return these from a service
        return api_helpers.listener_protocol_field_data(request)

    class Meta(object):
        name = _("Protocol Data")
        # TODO(mdurrant) - Add a10-specific permissions
        permissions = ("openstack.services.network", )
        help_text = _("Specify the details for the name and subnet of the VIP below")


class CreateSessionPersistenceAction(workflows.Action):
    # You can't do cookies in anything but HTTP/HTTPS.
    # You can do source IP (almost) everywhere.
    # TODO(mdurrant): Make this sucker dynamic - filter based on the protocol.
    session_persistence = forms.ChoiceField(label=_("Session Persistence"),
                                            widget=forms.Select(
                                            attrs=ui_helpers.switchable_field(
                                                "session_persistence")),
                                            required=True)
    cookie_name = forms.CharField(label=_("Cookie Name"), min_length=1, max_length=255,
                                  required=False)

    def populate_session_persistence_choices(self, request, context):
        # TODO(mdurrant): Get these from web service
        return api_helpers.session_persistence_field_data(request)

    class Meta(object):
        name = _("Session Persistence")
        # TODO(mdurrant) - Add a10-specific permissions
        permissions = ("openstack.services.network", )
        help_text = _("Define session persistence for the LB pool.")


class CreateLbStep(workflows.Step):
    action_class = CreateLbAction
    contributes = ("lb_name", "lb_description", "vip_subnet", "admin_state_up")


class CreateListenerStep(workflows.Step):
    action_class = CreateListenerAction
    # TODO(mdurrant): Add SSL data
    # TODO(mdurrant): Support all A10 protocols
    contributes = ("loadbalancer_id", "description", "listener_name", "protocol", "protocol_port")

    def prepare_action_context(self, request, context):
        super(CreateListenerStep, self).prepare_action_context(request, context)


class CreateVipStep(workflows.Step):
    action_class = CreateVipAction
    # TODO(mdurrant): Add SSL data
    # TODO(mdurrant): Support all A10 protocols
    contributes = ("protocol", "protocol_port")


class CreatePoolStep(workflows.Step):
    action_class = CreatePoolAction
    # TODO(mdurrant): Support all A10 LBs.
    # the pool protocol merely acts as a constraint on persistence
    contributes = ("pool_name", "description", "listener_id", "lb_algorithm", "pool_protocol",
                   "session_persistence", "cookie_name")


class CreateMemberStep(workflows.Step):
    action_class = CreateMemberAction
    # TODO(mdurrant) - Refactor Create*Steps as mixins so individual steps can be used
    # for "create the LB graph" and "create a single element"
    contributes = ("name", "weight", "member_subnet_id", "member_address", "member_protocol_port",
                   "admin_state_up", "pool_id")


class CreateSessionPersistenceStep(workflows.Step):
    action_class = CreateSessionPersistenceAction
    contributes = ("session_persistence", "cookie_name")


class CreateHealthMonitorStep(workflows.Step):
    action_class = CreateHealthMonitorAction
    contributes = ("pool_id", "monitor_type", "delay", "timeout", "http_method", "url_path",
                   "expected_codes", "max_retries", "admin_state_up")


class CreateCertificateStep(workflows.Step):
    action_class = CreateCertificateAction
    contributes = ("cert_name", "cert_data", "key_data", "intermediate_data", "password")


class SpecifyCertificateStep(workflows.Step):
    action_class = SpecifyCertificateAction
    contributes = ("use_tls", "description", "certificate_id", "cert_data",
                   "key_data", "intermediate_data", "password")


class CreateLoadBalancerWorkflow(workflows.Workflow):
    slug = "createlb"
    name = _("Create Load Balancer")
    default_steps = (CreateLbStep,)
    success_url = "horizon:project:a10vips:index"
    finalize_button_name = "Create Load Balancer"

    def handle(self, request, context):
        try:
            lb_body = from_ctx.get_lb_body_from_context(context)
            lbaasv2.create_loadbalancer(request, lb_body)
            return True
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(request, _("Could not create load balancer"))
            return False


class CreateListenerWorkflow(workflows.Workflow):
    slug = "createlistener"
    name = _("Create Listener")
    default_steps = (CreateListenerStep, SpecifyCertificateStep,)
    success_url = "horizon:project:a10vips:index"
    finalize_button_name = "Create Listener"

    def get_initial(self):
        return super(CreateListenerWorkflow, self).get_initial()

    def handle(self, request, context):
        try:
            rollback = []

            body = from_ctx.get_listener_body_from_context(context)
            cert_body = from_ctx.get_cert_body_from_context(context)

            use_tls = context.get("use_tls", False)
            if use_tls:
                cert = certificates.create_certificate(request, cert_body)
                rollback.append((cert.get("id"), certificates.delete_certificate))

            listener = lbaasv2.create_listener(request, body)
            rollback.append((listener.get("id"), lbaasv2.delete_listener))

            if use_tls:
                binding = certificates.create_binding(request, listener.get("id"), cert.get("id"))
                rollback.append((binding.get("id"), certificates.delete_binding))
            return True
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(request, _("Could not create Listener"))
            for rb in rollback:
                f = rb[1]
                v = rb[0]

                try:
                    f(request, v)
                except Exception as ex:
                    LOG.exception(ex)


class CreatePoolWorkflow(workflows.Workflow):
    slug = "createpool"
    name = _("Create Pool")
    default_steps = (CreatePoolStep, CreateSessionPersistenceStep, )
    success_url = reverse_lazy(SUCCESS_URL)
    finalize_button_name = "Create Pool"

    def handle(self, request, context):
        try:
            body = from_ctx.get_pool_body_from_context(context)
            lbaasv2.pool_create(request, **body.get("pool"))
            return True
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(request, _("Could not create pool"))
        return False

    def validate(self, context):
        protocol_error_msg = "Listener Protocol {0} cannot be used with Pool Protocol {1}"

        listener_id = context.get("listener_id")
        pool_protocol = context.get("pool_protocol")

        if listener_id:
            listener = lbaasv2.show_listener(self.request, context.get("listener_id"))
            listener_protocol = listener.get("protocol")
            valid_protocols = LISTENER_POOL_PROTOCOLS.get(listener_protocol, [])
            if pool_protocol not in valid_protocols:
                err_msg = protocol_error_msg.format(listener_protocol, pool_protocol)
                # TODO(mdurrant) - Get steps by name, something other than index.
                self.steps[0].add_step_error(_(str(err_msg)))
                exceptions.handle(self.request,
                                  exceptions.WorkflowValidationError(protocol_error_msg.format(
                                      listener_protocol, pool_protocol)))
                return False

        return True


class CreateMemberWorkflow(workflows.Workflow):
    slug = "createmember"
    name = _("Create Member")
    default_steps = (CreateMemberStep,)
    success_url = reverse_lazy(SUCCESS_URL)
    # success_url = SUCCESS_URL
    # redirect_url = "horizon:project:a10scaling:index"
    detail_url = "horizon:project:a10vips:pooldetail"
    finalize_button_name = "Create Member"
    success_message = _("Added Member")
    failure_message = _("Failed to add member")

    def handle(self, request, context):
        try:
            if context:
                pool_id = context.pop("pool_id")
                self.success_url = reverse_lazy(self.detail_url, kwargs={"id": pool_id})
                body = from_ctx.get_member_body(context, pool_id)
                lbaasv2.member_create(request, pool_id, body)
                return True
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(request, _("Could not create member"))
        return False


class CreateHealthMonitorWorkflow(workflows.Workflow):
    slug = "createmonitor"
    name = _("Create Health Monitor")
    default_steps = (CreateHealthMonitorStep,)
    success_url = reverse_lazy(SUCCESS_URL)
    finalize_button_name = "Create Health Monitor"

    def handle(self, request, context):
        try:
            body = from_ctx.get_monitor_body(context)
            lbaasv2.healthmonitor_create(request, **body.get("healthmonitor"))

            return True
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(request, _("Could not create health monitor"))
        return False


class CreateCertificateWorkflow(workflows.Workflow):
    slug = "createcertificate"
    name = _("Create Certificate")
    default_steps = (CreateCertificateStep,)
    success_url = SUCCESS_URL
    finalize_button_name = "Create Certificate"

    def handle(self, request, context):
        try:
            body = from_ctx.get_cert_body_from_context(context)
            cert = certificates.create_certificate(request, body)
            return True
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(request, _("Could not certificate"))
        return False


class SpecifyCertificateWorkflow(workflows.Workflow):
    slug = "specifycert"
    name = _("Specify or Create a Certificate")
    success_url = SUCCESS_URL
    finalize_button_name = "Create Certificate"


class CreateVipWorkflow(workflows.Workflow):
    slug = "addvip"
    name = _("Create VIP")
    # TODO(mdurrant): Add Certificate step that is selected when the user selects "Secure"
    default_steps = (CreateLbStep,
                     CreateVipStep,
                     CreatePoolStep,
                     CreateSessionPersistenceStep,)

    success_url = SUCCESS_URL
    finalize_button_name = "Create VIP"

    def handle(self, request, context):
        # First, try to create the LB.
        # Make sure we get an IP back because we need it for the listener.
        # Then, try to create the listener.
        # If we fail, delete the LB.
        success = False
        lb = None
        # A list of tuples consisting of the id of the item and the call
        # needed to remove it in the event of failure.
        # This allows graceful failure without needing to clean things up manually
        cleanup_stack = []

        try:
            lb_body = from_ctx.get_lb_body_from_context(context)
            lb = lbaasv2.create_loadbalancer(request, lb_body)
            lb_id = lb.get("id")
            cleanup_stack.append((lbaasv2.loadbalancer_delete, lb_id, "loadbalancer"))

            listener_body = from_ctx.get_listener_body_from_context(context, lb_id)
            listener = lbaasv2.create_listener(request, listener_body)
            listener_id = listener.get("id")
            cleanup_stack.append((lbaasv2.delete_listener, listener_id, "listener"))

            pool_body = from_ctx.get_pool_body_from_context(context, listener_id)
            pool = lbaasv2.pool_create(request, **pool_body.get("pool"))
            pool_id = pool.get("id")
            cleanup_stack.append((lbaasv2.pool_delete, pool_id, "pool"))

            # If we got this far, we succeeded!
            success = True

        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(request, _("Could not create listener"))

        if not success:
            while len(cleanup_stack) > 0:
                cleanup_call, obj_id, obj_type = cleanup_stack.pop()
                try:
                    cleanup_call(request, obj_id)
                except Exception as ex:
                    LOG.exception(ex)
                    exceptions.handle(request, _("Could not delete {} {}") % (obj_type, obj_id))
        return successs
