from django.db import models


class News(models.Model):
    news_id = models.IntegerField(primary_key=True)
    header = models.CharField(max_length=256)
    link = models.URLField(max_length=200)
    img = models.ImageField()
    text = models.TextField()
