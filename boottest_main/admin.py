from django.contrib import admin
from .models import TestRecord, BackgroundJob


@admin.register(TestRecord)
class TestRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "num_value", "text_value", "created")


@admin.register(BackgroundJob)
class BackgroundJobAdmin(admin.ModelAdmin):
    list_display = ("id", "method", "args", "start_time", "job_id", "end_time",
                    "result")
