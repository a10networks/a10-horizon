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


from django.apps import AppConfig


class A10NetworksProjectConfig(AppConfig):
    name = 'a10_horizon.dashboard.project'
    label = 'a10networks'
    verbose_name = "A10 Networks"


class A10NetworksAdminConfig(AppConfig):
    name = 'a10_horizon.dashboard.admin'
    label = 'a10admin'
    verbose_name = "A10 Networks - Admin"


class A10NetworksResourcesConfig(AppConfig):
    name = 'a10_horizon.dashboard.a10networks'
    label = "a10horizon_resources"
    verbose_name = "Non-Viewable Application - A10 Networks Shared Resources"
