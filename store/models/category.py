from django.db import models

class Category(models.Model):
    category_name = models.CharField(max_length=255, null=True, blank=True)
    category_image = models.ImageField(upload_to='categories/', null=True, blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name

