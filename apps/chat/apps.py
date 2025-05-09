from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.chat'

    def ready(self):
        print("ChatConfig ready method called - importing signals")
        import apps.chat.signals
        print("Signals imported successfully")