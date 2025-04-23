from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from apps.chat.models import Message, Conversation

User = get_user_model()

class MessageSendTests(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(email='sender@example.com', password='pass1234')
        self.receiver = User.objects.create_user(email='receiver@example.com', password='pass1234')

        self.url = reverse('message-send')  

    @patch('apps.chat.views.GetStreamService')
    def test_send_message_successfully(self, mock_stream_service):
        self.client.force_authenticate(user=self.sender)

        mock_channel = mock_stream_service.return_value.create_or_get_channel.return_value
        mock_stream_service.return_value.send_message.return_value = None

        data = {
            'receiver': self.receiver.id,
            'content': 'Hello there!'
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['sender'], self.sender.email)
        self.assertEqual(response.data['data']['receiver'], self.receiver.email)
        self.assertEqual(response.data['data']['content'], 'Hello there!')

    def test_missing_content_or_receiver(self):
        self.client.force_authenticate(user=self.sender)

        # Missing receiver
        response1 = self.client.post(self.url, {'content': 'Missing receiver'})
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing content
        response2 = self.client.post(self.url, {'receiver': self.receiver.id})
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_receiver_does_not_exist(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.post(self.url, {'receiver': 9999, 'content': 'Hello'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_cannot_send_message(self):
        data = {'receiver': self.receiver.id, 'content': 'Hi!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.chat.views.GetStreamService')
    def test_reuses_existing_conversation(self, mock_stream_service):
        self.client.force_authenticate(user=self.sender)

        conversation = Conversation.objects.create()
        conversation.participants.set([self.sender, self.receiver])

        data = {
            'receiver': self.receiver.id,
            'content': 'Second message'
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)  # No new conversation created
        self.assertEqual(Message.objects.count(), 1)
