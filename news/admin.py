from django.contrib import admin
from .models import News


class NewsAdmin(admin.ModelAdmin):
    """
    Admin for the news app
    """
    list_display = ('title', 'slug', 'status', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(News, NewsAdmin)
