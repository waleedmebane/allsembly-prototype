from django.db import models

class RegistrationComment(models.Model):
    username = models.CharField(primary_key=True, max_length=150)
    real_name = models.CharField(max_length=255)
    email_address = models.EmailField()
    comment = models.TextField()
