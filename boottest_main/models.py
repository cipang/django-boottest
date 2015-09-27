from django.db import models


class TestRecord(models.Model):
    num_value = models.DecimalField(max_digits=6, decimal_places=3)
    text_value = models.CharField(max_length=50)
    created = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{0}".format(self.id)

    class Meta:
        ordering = ("-num_value",)


class BackgroundJob(models.Model):
    method = models.CharField("Method", max_length=50)
    args = models.CharField("Args", max_length=200, blank=True, default="")
    start_time = models.DateTimeField("Start Time")
    job_id = models.CharField("Job ID", max_length=100, blank=True, default="")
    result = models.CharField("Result", max_length=200, blank=True, default="")
    end_time = models.DateTimeField("End Time", null=True, blank=True,
                                    default=None)
    error = models.TextField("Error", blank=True, default="")

    def __str__(self):
        return "{0}".format(self.id)

    class Meta:
        ordering = ("-id",)
