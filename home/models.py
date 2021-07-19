from django.db import models

# Create your models here.

class Tweet(models.Model):
    search=models.CharField(max_length=100,default="")
    date=models.CharField(max_length=10,default="")
    clean_tweets=models.TextField()
    def __str__(self):
        return self.search + "      " + self.date


class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    subject=models.CharField(max_length=300)
    message=models.TextField()
    date = models.DateField()
    def __str__(self):
        return self.name


