from django.contrib import admin


class AdminSite(admin.AdminSite):
    site_title = "Macau"
    site_header = "Macau administration"


admin_site = AdminSite()
