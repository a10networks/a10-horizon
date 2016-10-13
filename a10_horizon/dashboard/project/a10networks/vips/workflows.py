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

# TODO(mdurrant) - Remove the debugging crap
CERT_DATA = """-----BEGIN CERTIFICATE-----
MIID1zCCAr+gAwIBAgIJAIUmrLlxfBYIMA0GCSqGSIb3DQEBCwUAMIGBMQswCQYD
VQQGEwJVUzELMAkGA1UECAwCSUQxDjAMBgNVBAcMBUJvaXNlMRwwGgYDVQQKDBNB
MTAgTmV0d29yayBUZXN0aW5nMRUwEwYDVQQLDAxTb2Z0d2FyZSBEZXYxIDAeBgNV
BAMMF3NzbHRlc3QuYTEwbmV0d29ya3MuY29tMB4XDTE2MTAxMTIwMDYyOVoXDTI2
MTAwOTIwMDYyOVowgYExCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJJRDEOMAwGA1UE
BwwFQm9pc2UxHDAaBgNVBAoME0ExMCBOZXR3b3JrIFRlc3RpbmcxFTATBgNVBAsM
DFNvZnR3YXJlIERldjEgMB4GA1UEAwwXc3NsdGVzdC5hMTBuZXR3b3Jrcy5jb20w
ggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDbnD5CiARaiDAjd53AGwtO
DG0fbPOldi8/anCyZWA2/lPlbBvSGBZtNjAtG+a6jGQhxlp27K3yheuF0jZeBpFk
adBMSUQYCYfNeMFn2n8JThO8k1IfAheKxzAzjq454ieAOjTuUkVLHWV74mkfmE7e
qJWEen3idoJahmofWKLFXB3g/r2vyjVAllka1r37N6YNbO3EPE3SVGdHylQSlXI8
ajenHgiSf+luhzsfx5/o+cuSUhmFD5i1J0AHdtcgdd+OXR/11dG4fy3oir+8cbaV
dwaXP65ra5W7b3nOeI4JO1N7Aa1z8Mtbb1J16QRHJT/ekCh+OF5HNrkmXZLD0jRL
AgMBAAGjUDBOMB0GA1UdDgQWBBRmg1gbMqCOxj5atETfBYp4e/pyLzAfBgNVHSME
GDAWgBRmg1gbMqCOxj5atETfBYp4e/pyLzAMBgNVHRMEBTADAQH/MA0GCSqGSIb3
DQEBCwUAA4IBAQA8XsLizv4KiO0PGK+k7zF5xJ9ogVZdkjY+CgXlop0xTq+Kt7n1
+6EPorS7HNYiltC4pr5OjcMhDtKORloV0ATSa5K27dyzYYw6v1cfVOiivixyT6dY
hm9EZs+gYt8kVo1mAfb0g6zqRJy3gkMVkhsb4DlxPRNcKMX1bLrfisrRfc6yDH6D
dZBK63BSYh7H8wHh1CE6kBjdNOFDL4nJIRup/mtCZETU7z/FFvnEqaBDkIKVQ4dk
LyUPKyQcM6tFc6WjHTx/YOuih4gaupzJDCMWjyWrrNxNIaTZziRSuCggLs4b3LQD
j84tU5/SsueWoIXdCcogq9Szn/UjfJGi9n1s
-----END CERTIFICATE-----"""

KEY_DATA = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDbnD5CiARaiDAj
d53AGwtODG0fbPOldi8/anCyZWA2/lPlbBvSGBZtNjAtG+a6jGQhxlp27K3yheuF
0jZeBpFkadBMSUQYCYfNeMFn2n8JThO8k1IfAheKxzAzjq454ieAOjTuUkVLHWV7
4mkfmE7eqJWEen3idoJahmofWKLFXB3g/r2vyjVAllka1r37N6YNbO3EPE3SVGdH
ylQSlXI8ajenHgiSf+luhzsfx5/o+cuSUhmFD5i1J0AHdtcgdd+OXR/11dG4fy3o
ir+8cbaVdwaXP65ra5W7b3nOeI4JO1N7Aa1z8Mtbb1J16QRHJT/ekCh+OF5HNrkm
XZLD0jRLAgMBAAECggEAFUj/f9NPGLc6czWUxJnabqYlrXYR52edDLh0U9YfjTT5
TLM9vw82nT8zTCv4IPyad+uRuRUXhvoT6dSGEHbygJkA52PyhaHm17Nsi3RR+8Tl
hNGClB7PyVOlCFo76MBSs8rwdmji7nTa8TbwmW9ZtZsBYuW8bcauu7drcb5ViGtH
I1mJycZ2RxDvpXvWpRClwfFiJTEpBgxYo8psaFkUFQqht2j3hD7kyuzpxO9xpjsh
Wl2Eee0p8b2QVmiCT/LgqB8d9Z3VCdew4r2Un99PfO7q4OFcWwJ3s1Y0apQQ914E
MoTgITBM7COhaVAnKPGa/xvJTqSZ0wEoYI5YXK2EAQKBgQD/U3xhTJGisNdMCsuo
WSXRmHby9GNp+Ut2PzhbxY5HovDGNauiIlkVFelUQ18XGE0tlYKiFTv15XbKNatB
qr7uATTrV1f8IWrlUOwhrrTQyJPay6m0MvbfX7Y7uBEi4t1bHaU8/JYR6iYvG2pX
cuArwmVoStJRedCOmCIYGW106wKBgQDcMKAjgim9OGcVL9J+tHnbchf9xWWJR7r4
HwQZE2qddMVC7sJnMf0yGLWSUBuIlh+8t9vD31E5GjAN1z4DYs4iHZwH70QDtYSy
keC9G8QEQk/VZTVdBtnXp+YRj++ol+Y1mkE/2+530A3pcQBEpNfxQpV0VajFkFeF
aI+X4kHmIQKBgQDjFqzsmT56tdB3eK6UZ93EIlfBVO3KxoiAflAxB2+5dUmy8O9b
gDM9FsT1RgqgLuQN5AlRAZPX66QQy1UrTaMNapNXsdK2lD5QAP5UIt/9RjiDBFtG
w4FhQO6DBP5wydhY/vAFYx5ShrA5e6fEaY7KPNcWwF15S9/bw6GnT45TywKBgGrw
PsYgEE9y1jWm/S9GTaxzdA1u0kpjCP46ag4XrP792FQSi139HEA5We3OdCDY8F8C
WHx/t/3opxAByn9wfDZ7dO0xmjHG9cSYLrMJiiCbaBR2y/z7N8+SHp3G7xlNdKPx
3+C42s9bv3XxyLSN7saglN9kPsx8ttT3HE4it+ihAoGBANvIAPjKySNPcbz6eeYE
pLLzK0l5oRNPGnqOj6N5Njy5IWz/T0MRB1Mh/w0zNk9EQbdhzV5Lm71cuNOZb93W
5vxpPBxWyAWBjlaPiPxz0AmjKPrXsRekyTsBe8HJ1Bk8/qSY8k0Gk8yKgPm2Je3L
Rv4a8yRehRRjWFxwExTtwFwh
-----END PRIVATE KEY-----"""


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
        return {
            "class": "switched",
            "data-switch-on": "monitor_type",
            "data-monitor_type-http": title,
            "data-monitor_type-https": title,
        }

    pool_id = forms.ChoiceField(label=_("Pool"), required=True)
    monitor_type = forms.ChoiceField(label=_("Monitor Type"), required=True,
                                     widget=forms.Select(
                                     attrs={"class": "switchable", "data-slug": "monitor_type"}))

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

        if dev_debug:
            self.fields["cert_name"].initial = self._random_name()
            self.fields["cert_data"].initial = CERT_DATA
            self.fields["key_data"].initial = KEY_DATA
            self.fields["password"].initial = ""

    def textarea_size(rows=10, cols=25):
        """
            Returns default style attributes for text inputs
            Makes code cleaner by not having these littered everywhere
        """
        return {
            "cols": cols,
            "rows": rows
        }

    """
        Specify an existing certificate or create a new one.
    """
    # TODO(mdurrant) Create a validator for cert data using cryptography lib
    cert_name = forms.CharField(label=_("Name"),
                                help_text="Specify a name for the certificate data",
                                widget=forms.Textarea(attrs=textarea_size(rows=1)))
    cert_data = forms.CharField(label=_("Certificate Data"), required=False,
                                widget=forms.Textarea(
                                    attrs=textarea_size()),
                                min_length=1, max_length=8000)
    key_data = forms.CharField(label=_("Key Data"), required=False,
                               widget=forms.Textarea(attrs=textarea_size()),
                               min_length=1, max_length=8000)
    intermediate_data = forms.CharField(label=_("Intermediate Data"), required=False,
                                        widget=forms.Textarea(
                                            attrs=textarea_size()),
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

    def _random_name(self):
        import random
        chars = []
        for n in range(1, 16):
            chars.append(chr(random.randint(65, 90)))
        return "".join(chars)

    def _populate_debug_defaults(self):
        dev_debug = horizon_conf.HORIZON_CONFIG.get("debug")

        if dev_debug:
            self.fields["cert_name"].initial = self._random_name()
            self.fields["cert_data"].initial = CERT_DATA
            self.fields["key_data"].initial = KEY_DATA
            self.fields["password"].initial = ""

    def textarea_size(rows=10, cols=25):
        """
            Returns default style attributes for text inputs
            Makes code cleaner by not having these littered everywhere
        """
        return {
            "cols": cols,
            "rows": rows
        }

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

    certificate_id = forms.ChoiceField(label=_("Select an existing certificate"),
                                       widget=forms.Select(
        attrs=ui_helpers.switchable_field("certificate_id")))

    cert_name = forms.CharField(label=_("Name"),
                                help_text="Specify a name for the certificate data",
                                widget=forms.Textarea(attrs=hide_create_controls("Name", textarea_size(rows=1))))
    cert_data = forms.CharField(label=_("Certificate Data"), required=False,
                                widget=forms.Textarea(
                                    attrs=hide_create_controls("Certificate Data", textarea_size())),
                                min_length=1, max_length=8000)
    key_data = forms.CharField(label=_("Key Data"), required=False,
                               widget=forms.Textarea(attrs=hide_create_controls(
                                   "Private Key", textarea_size())),
                               min_length=1, max_length=8000)
    intermediate_data = forms.CharField(label=_("Intermediate Data"), required=False,
                                        widget=forms.Textarea(
                                            attrs=hide_create_controls("Intermediate Data", textarea_size())),
                                        min_length=1, max_length=8000)
    password = forms.CharField(widget=forms.PasswordInput(
        render_value=False, attrs=hide_create_controls("Password", textarea_size(rows=1))), required=False)

    def __init__(self, request, context, *args, **kwargs):
        super(SpecifyCertificateAction, self).__init__(request, context, *args, **kwargs)
        self._set_control_attributes()
        self._populate_debug_defaults()

    def _random_name(self):
        import random
        chars = []
        MAX_CHARS = 16
        MIN_CHARS = 8
        CHAR_LOWER_BOUND = ord('A')
        CHAR_UPPER_BOUND = ord('Z')

        for n in range(1, random.randint(MIN_CHARS, MAX_CHARS)):
            chars.append(chr(random.randint(CHAR_LOWER_BOUND, CHAR_UPPER_BOUND) +
                             (32 if bool(random.randint(0, 2)) else 0)))
        return "".join(chars)

    def switched_field(data_slug, title_mappings):
        """
            Beginning of abstracting the above.
        """
        rv = {
            "class": "switched",
            "data-switch-on": data_slug
        }

        for k, v in title_mappings.iteritems():
            attr_key = "data-{0}-{1}".format(data_slug, k)
            attr_val = v
            rv[attr_key] = attr_val

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
                                            attrs={"class": "switchable",
                                                   "data-slug": "session_persistence"}),
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
    contributes = ("loadbalancer_id", "name", "protocol", "protocol_port")

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
    contributes = ("listener_id", "lb_algorithm", "pool_protocol", "session_persistence",
                   "cookie_name")


class CreateMemberStep(workflows.Step):
    action_class = CreateMemberAction
    # TODO(mdurrant) - Refactor Create*Steps as mixins so individual steps can be used
    # for "create the LB graph" and "create a single element"
    contributes = ("weight", "member_subnet_id", "member_address", "member_protocol_port",
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
    contributes = ("certificate_id", "cert_data", "key_data", "intermediate_data", "password")


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
            body = from_ctx.get_listener_body_from_context(context)
            cert_body = from_ctx.get_cert_body_from_context(context)

            listener = lbaasv2.create_listener(request, body)
            cert = certificates.create_certificate(request, cert_body)
            binding = certificates.create_binding(request, listener.get("id"), cert.get("id"))
            return True
        except Exception as ex:
            LOG.exception(ex)
            exceptions.handle(request, _("Could not create Listener"))


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
    success_url = URL_PREFIX + "createmonitor"
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
        return success
