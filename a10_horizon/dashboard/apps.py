

from django.apps import AppConfig

class A10NetworksProjectConfig(AppConfig):
    name = 'a10_horizon.dashboard.project'
    label = 'a10networks'
    verbose_name = "A10 Networks"


class A10NetworksAdminConfig(AppConfig):
    name = 'a10_horizon.dashboard.admin'
    label = 'a10admin'
    verbose_name = "A10 Networks - Admin"
