# Copyright (C) 2016, A10 Networks Inc. All rights reserved.
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
from openstack_dashboard.local import local_settings
import a10_horizon

PANEL_GROUP = 'a10networks_project'
PANEL_GROUP_NAME = 'A10 Networks'
PANEL_DASHBOARD = "project"
PANEL_GROUP_DASHBOARD = PANEL_DASHBOARD
ADD_INSTALLED_APPS = ['a10_horizon.dashboard.project.a10networks']
AUTO_DISCOVER_STATIC_FILES = True
