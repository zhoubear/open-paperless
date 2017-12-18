from __future__ import unicode_literals

from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'submit_date'
    list_display = ('document', 'submit_date', 'user', 'comment')
    list_filter = ('user',)
    readonly_fields = ('document', 'submit_date', 'user', 'comment')
    search_fields = ('comment',)
