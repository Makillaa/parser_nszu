from rest_framework import serializers
from .models import News


class NewsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['header', 'link', 'img', 'text']