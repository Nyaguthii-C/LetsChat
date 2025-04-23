from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.chat.models import Message, Conversation  # adjust import if needed

User = get_user_model()

class MessageActionTests(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(email='sender@example.com', password='pass1234')
        self.receiver = User.objects.create_user(email='receiver@example.com', password='pass1234')
        self.other_user = User.objects.create_user(email='other@example.com', password='pass1234')

        self.conversation = Conversation.objects.create()
        self.conversation.participants.set([self.sender, self.receiver])

        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Original message',
            conversation=self.conversation
        )

    def test_sender_can_delete_message(self):
        self.client.force_authenticate(user=self.sender)
        url = reverse('message-delete', kwargs={'pk': self.message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_sender_cannot_delete_message(self):
        self.client.force_authenticate(user=self.receiver)
        url = reverse('message-delete', kwargs={'pk': self.message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("not authorized", str(response.data).lower())

    def test_delete_nonexistent_message(self):
        self.client.force_authenticate(user=self.sender)
        url = reverse('message-delete', kwargs={'pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_sender_can_update_message(self):
        self.client.force_authenticate(user=self.sender)
        url = reverse('message-update', kwargs={'pk': self.message.id})
        response = self.client.patch(url, data={'content': 'Updated message'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['content'], 'Updated message')

    def test_non_sender_cannot_update_message(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('message-update', kwargs={'pk': self.message.id})
        response = self.client.patch(url, data={'content': 'Hacked message'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_without_content(self):
        self.client.force_authenticate(user=self.sender)
        url = reverse('message-update', kwargs={'pk': self.message.id})
        response = self.client.patch(url, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('required', str(response.data).lower())

    def test_update_nonexistent_message(self):
        self.client.force_authenticate(user=self.sender)
        url = reverse('message-update', kwargs={'pk': 999})
        response = self.client.patch(url, data={'content': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
