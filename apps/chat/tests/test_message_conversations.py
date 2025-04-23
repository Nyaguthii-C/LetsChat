from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.chat.models import Conversation

User = get_user_model()

class ConversationTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', password='password')
        self.user2 = User.objects.create_user(email='user2@example.com', password='password')
        self.user3 = User.objects.create_user(email='user3@example.com', password='password')

        # URLs for the views
        self.conversation_list_url = reverse('conversation-list-create')
        self.conversation_detail_url = reverse('conversation-detail', kwargs={'pk': 1})

    def test_conversation_list_authenticated(self):
        """Test that an authenticated user can retrieve their conversations."""
        self.client.force_authenticate(user=self.user1)

        # Creating a conversation where user1 and user2 are participants
        conversation = Conversation.objects.create()
        conversation.participants.set([self.user1, self.user2])

        # A GET request to retrieve the conversations
        response = self.client.get(self.conversation_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One conversation in the list
        self.assertIn(self.user1.email, response.data[0]['participants'])



    def test_conversation_list_unauthenticated(self):
        """Test that an unauthenticated user cannot retrieve conversations."""
        response = self.client.get(self.conversation_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_conversation(self):
        """Test that an authenticated user can create a conversation."""
        self.client.force_authenticate(user=self.user1)

        # Creating a new conversation with participants
        data = {
            'participants': [self.user1.email, self.user2.email],
        }
        response = self.client.post(self.conversation_list_url, data, format='json')
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['participants']), 2)  # Two participants: user1 and user2
        self.assertIn(self.user1.email, response.data['participants'])


    def test_create_conversation_missing_participant(self):
        """Test that creating a conversation without participants fails."""
        self.client.force_authenticate(user=self.user1)

        # Missing participants
        data = {}
        response = self.client.post(self.conversation_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_conversation_detail(self):
        """Test that a user can retrieve a conversation detail."""
        self.client.force_authenticate(user=self.user1)

        # Creating a conversation and adding participants
        conversation = Conversation.objects.create()
        conversation.participants.set([self.user1, self.user2])

        # retrieving the conversation detail
        url = reverse('conversation-detail', kwargs={'pk': conversation.id})
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user1.email, response.data['participants'])




    def test_conversation_detail_unauthorized(self):
        """Test that an unauthorized user cannot retrieve a conversation detail."""
        self.client.force_authenticate(user=self.user3)

        # Creating a conversation with user1 and user2
        conversation = Conversation.objects.create()
        conversation.participants.set([self.user1, self.user2])

        url = reverse('conversation-detail', kwargs={'pk': conversation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_conversation_detail_not_found(self):
        """Test that trying to retrieve a non-existing conversation returns 404."""
        self.client.force_authenticate(user=self.user1)

        # Trying to access a non-existing conversation (ID 9999)
        url = reverse('conversation-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
