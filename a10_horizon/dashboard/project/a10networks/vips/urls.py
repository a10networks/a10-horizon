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

from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf import settings
from django.conf.urls import static

import a10_horizon
import views


urlpatterns = patterns("a10_horizon.dashboard.project.a10networks.vips.views",
    url(r'^$', views.IndexView.as_view(), name='index'),
    # Vips
    url(r'^create/$',
        views.CreateVipView.as_view(),
        name="create"),
    # url(r'^edit/(?P<id>[^/]*)$',
    #     views.EditVipView.as_view(),
    #     name="edit"),
    # LBs
    url(r'lb/create/$',
        views.CreateLoadBalancerView.as_view(),
        name="createlb"),
    url(r'lb/edit/(?P<id>[^/]*)$',
        views.UpdateLoadBalancerView.as_view(),
        name="editlb"),
    url(r'lb/detail/(?P<id>[^/]*)$',
        views.LBDetailView.as_view(),
        name="lbdetail"),
    # Listeners
    url(r'listener/create/$',
        views.CreateListenerView.as_view(),
        name="createlistener"),
    url(r'listener/edit/(?P<id>[^/]*)$',
        views.UpdateListenerView.as_view(),
        name="editlistener"),
    url(r'listener/detail/(?P<id>[^/]*)$',
        views.ListenerDetailView.as_view(),
        name="listenerdetail"),
    # Pools
    url(r'^pool/detail/(?P<id>[^/]*)$',
        views.PoolDetailView.as_view(),
        name="pooldetail"),
    url(r'pool/create/$',
        views.CreatePoolView.as_view(),
        name="createpool"),
    url(r'pool/edit/(?P<id>[^/]*)$',
        views.UpdatePoolView.as_view(),
        name="editpool"),
    # Members
    url(r'pool/(?P<pool_id>[^/]+)/member/(?P<id>[^/]+)/detail$',
        views.MemberDetailView.as_view(),
        name="memberdetail"),
    url(r'pool/(?P<pool_id>[^/]*)/member/create$',
        views.CreateMemberView.as_view(),
        name="createmember"),
    url(r'pool/(?P<pool_id>[^/]+)/member/(?P<id>[^/]+)/edit$',
        views.UpdateMemberView.as_view(),
        name="editmember"),
    # HMs
    url(r'healthmonitor/detail/(?P<id>[^/]+)$',
        views.MonitorDetailView.as_view(),
        name="monitordetail"),
    url(r'healthmonitor/create$',
        views.CreateMonitorView.as_view(),
        name="createmonitor"),
)

# (?P<instance_id>[^/]+)/(?P<keypair_name>[^/]+)/$
