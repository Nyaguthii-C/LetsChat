# `python manage.py shell < test_signals.py`

from django.dispatch import Signal
from django.db.models import signals
from apps.chat.models import Message

print("Checking for registered signals on Message model...")

# Get all registered signal receivers
post_save_receivers = signals.post_save.receivers

# Check for your specific receiver
message_receivers = [r for r in post_save_receivers if r[0][0] == Message]

print(f"Found {len(message_receivers)} receivers for Message model on post_save signal.")
for idx, receiver in enumerate(message_receivers):
    print(f"Receiver {idx+1}: {receiver}")

print("\nYou should see at least one receiver if your signal is properly connected.")