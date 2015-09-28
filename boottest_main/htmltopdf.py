import logging
import django_rq
import rq
import os
import subprocess
from django.utils.timezone import now
from django.template.loader import render_to_string
from tempfile import NamedTemporaryFile
from .models import TestRecord, BackgroundJob


logger = logging.getLogger("django")


@django_rq.job("low")
def generate_pdf(record_pk):
    try:
        logger.info("Loading PDF job information...")
        job = BackgroundJob.objects.get(id=record_pk)
        rq_job = rq.get_current_job()
        wkhtmltopdf = os.path.join(os.path.expanduser("~"),
                                   "bin",
                                   "wkhtmltopdf-linux-amd64")

        logger.info("Creating HTML from template...")
        f = NamedTemporaryFile(suffix=".html", delete=False)
        html_filename = f.name
        try:
            html = render_to_string("pdf.html",
                                    {"data": TestRecord.objects.all()[0:20],
                                     "job_id": rq_job.id})
            f.write(html.encode("utf-8"))
            f.flush()
        finally:
            f.close()

        logger.info("Creating temp file for the PDF...")
        pdf_filename = None
        with NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_filename = f.name

        logger.info("Call wkhtmltopdf...")
        result = subprocess.call(wkhtmltopdf, html_filename, pdf_filename).returncode

        job.result = str(result) + " " + str(os.stat(pdf_filename))
        job.end_time = now()
        job.save()
        return True
    except Exception:
        logger.exception("PDF error")
        return False
