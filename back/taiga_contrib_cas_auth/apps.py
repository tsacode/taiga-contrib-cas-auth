from django.apps import AppConfig


class TaigaContribCasAuthAppConfig(AppConfig):
    name = "taiga_contrib_cas_auth"
    verbose_name = "Taiga contrib cas auth App Config"

    def ready(self):
        from taiga.auth.services import register_auth_plugin
        from . import services
        register_auth_plugin("cas", services.cas_login_func)

