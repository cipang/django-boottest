import pdfkit
import logging
import django_rq
import rq
import os
from django.utils.timezone import now
from django.template.loader import render_to_string
from .models import TestRecord, BackgroundJob


logger = logging.getLogger("django")


@django_rq.job("low")
def generate_pdf(record_pk):
    try:
        job = BackgroundJob.objects.get(id=record_pk)
        rq_job = rq.get_current_job()

        html = render_to_string("pdf.html",
                                {"data": TestRecord.objects.all()[0:20],
                                 "job_id": rq_job.id})
        output_file = "/tmp/test_{0}.pdf".format(rq_job.id)
        wkhtmltopdf = os.path.join(os.path.expanduser("~"),
                                   "bin",
                                   "wkhtmltopdf-linux-amd64")
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf)
        pdfkit.from_string(html, output_file, configuration=config)

        job.result = output_file
        job.end_time = now()
        job.save()
        return True
    except Exception:
        logger.exception("PDF error")
        return False
