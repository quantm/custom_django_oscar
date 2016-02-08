#__author__ = 'tqn'
from oscar.apps.dashboard.app import DashboardApplication as CoreDashboardApplication
from .catalogue.app import application as dashboard_catalogue_app
from .partners.app import application as dashboard_partners_app


class DashboardApplication(CoreDashboardApplication):
    catalogue_app = dashboard_catalogue_app
    partners_app = dashboard_partners_app

application = DashboardApplication()