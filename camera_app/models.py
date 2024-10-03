# camera_app/models.py
from django.db import models

class Gesture(models.Model):
    gesture_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gesture_type
