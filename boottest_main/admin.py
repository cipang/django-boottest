from django.contrib import admin
from .models import TestRecord


@admin.register(TestRecord)
class TestRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "num_value", "text_value", "created")
