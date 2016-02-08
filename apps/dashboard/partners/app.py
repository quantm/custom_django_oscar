from oscar.apps.dashboard.partners.app import PartnersDashboardApplication as CorePartnersDashboardApplication
from .views import PartnerListView, PartnerUserSelectView, PartnerUserLinkView
class PartnersDashboardApplication(CorePartnersDashboardApplication):
    list_view = PartnerListView
    user_select_view = PartnerUserSelectView
    user_link_view = PartnerUserLinkView


application = PartnersDashboardApplication()