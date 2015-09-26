from django.db import models


class TestRecord(models.Model):
    num_value = models.DecimalField(max_digits=6, decimal_places=3)
    text_value = models.CharField(max_length=50)
    created = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{0}".format(self.id)

    class Meta:
        ordering = ("-num_value",)
