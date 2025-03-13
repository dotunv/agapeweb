from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class AgapeAdminSite(AdminSite):
    # Customize the admin site
    site_title = _('Agape Admin')
    site_header = _('Agape Administration')
    index_title = _('Welcome to Agape Admin')
    
    # Customize the admin site appearance
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        
        # Customize the order of apps
        app_ordering = {
            'users': 1,
            'subscriptions': 2,
            'transactions': 3,
            'auth': 4,
        }
        
        app_list.sort(key=lambda x: app_ordering.get(x['app_label'], 999))
        return app_list

# Create the custom admin site instance
admin_site = AgapeAdminSite(name='agape_admin') 