from .interfaces.notification_channel import INotificationChannel
from .properties.properties import TelegramNotificationProperties, NotificationChannelBaseProperties
from .channels.telegram_notification_channel import TelegramNotificationChannel

class NotificationService:

    def __init__(self, properties: NotificationChannelBaseProperties) -> None:
        self._channel = self._get_channel(properties)

    def _get_channel(self, properties: NotificationChannelBaseProperties) -> INotificationChannel:
        if isinstance(properties, TelegramNotificationProperties):
            return TelegramNotificationChannel(properties)
        else:
            raise Exception("Error: The communication channel does not exist")

    def send_notification(self, tittle: str, message: str):
        self._channel.send_message(tittle, message)