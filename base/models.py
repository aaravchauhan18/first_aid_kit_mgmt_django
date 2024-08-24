from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Medicine(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
    medicine_name = models.CharField(max_length = 200)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()

    def __str__(self):
        return self.medicine_name

    class Meta:
        ordering = ['expiry_date']