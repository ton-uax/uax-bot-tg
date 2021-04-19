"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = "api.dashboard.CustomIndexDashboard"

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = "api.dashboard.CustomAppIndexDashboard"
"""

from django.utils.translation import ugettext_lazy as _
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for api.
    """
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            _("Quick links"),
            layout="inline",
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                [_("Change password"),
                 reverse("%s:password_change" % site_name)],
                [_("Log out"), reverse("%s:logout" % site_name)],
            ]
        ))

        self.children.append(modules.ModelList(
            title=u"Пользователи",
            models=("core.apps.account.models.TelegramAccount",),
        ))
        
        self.children.append(modules.ModelList(
            title=u"Кошельки",
            models=("core.apps.wallet.models.Wallet",),
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(_("Recent Actions"), 5))

    