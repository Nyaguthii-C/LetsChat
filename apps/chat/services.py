from stream_chat import StreamChat
from django.conf import settings
from stream_chat.base.exceptions import StreamAPIException
from .models import CustomUser

class GetStreamService:
    def __init__(self):
        self.client = StreamChat(api_key=settings.GETSTREAM_API_KEY, api_secret=settings.GETSTREAM_API_SECRET)


    def create_or_get_channel(self, user_1, user_2):
        members = sorted([str(user_1.id), str(user_2.id)])
        channel_id = f"{members[0]}-{members[1]}"

        # Ensure all users exist in StreamChat
        for user in members:
            user = CustomUser.objects.get(id=user)  # Get user from Django DB
            self.create_user_in_streamchat(user)  # Create user in StreamChat


        # channel with type, ID, and data
        channel = self.client.channel(
            "messaging",
            channel_id,
            {
                "name": f"Chat between {user_1.full_name} and {user_2.full_name}",
                "members": members
            }
        )

        try:
            channel.create(str(user_1.id))  # user_id who initiates the channel
        except StreamAPIException as e:
            
            raise e

        return channel


    def send_message(self, channel, sender, receiver, content):
        """
        Send a message to the specified channel.
        """
        print(f'The gotten user ID is: {str(sender.id)}')

        message_payload = {
            "text": content
        }


        message = channel.send_message(message_payload, user_id=str(sender.id))
        return message

    def get_channel(self, user_1, user_2):
        """
        Retrieve the channel for the two users.
        """
        # try to get the existing channel
        return self.client.channel("messaging", f"{user_1.id}-{user_2.id}")



    def create_user_in_streamchat(self, user):
        """Create a user in StreamChat if they don't exist."""
        user_data = {
            "id": str(user.id), # Convert ID to string
            "name": user.full_name,
            "email": user.email,
            "role": "user",  # default role
        }
        self.client.upsert_user(user_data)  # Create or update user in StreamChat
