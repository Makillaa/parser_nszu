from rest_framework import generics
from .models import News
from .serializers import NewsListSerializer


class NewsListView(generics.ListAPIView):
    serializer_class = NewsListSerializer
    queryset = News.objects.all()
