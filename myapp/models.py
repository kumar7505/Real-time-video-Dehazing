from django.db import models

# Create your models here.
class User(models.Model):
    Name = models.CharField(max_length=50, default='')
    Mail = models.CharField(max_length=100, default='')
    Password = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.Name