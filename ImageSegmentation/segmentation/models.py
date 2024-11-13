from django.db import models
import uuid

# Create your models here.
class SegmentedImage(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_image_path = models.CharField(max_length=255)
    overlayed_image_path = models.CharField(max_length=255)
    predicted_image_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)