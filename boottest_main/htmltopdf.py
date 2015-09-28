import logging
import django_rq
import rq
import os
import subprocess
from django.utils.timezone import now
from django.template.loader import render_to_string
from tempfile import NamedTemporaryFile
from boto.s3.connection import S3Connection
from boto.s3.key import Key
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
        result = subprocess.call([wkhtmltopdf, "-q", html_filename,
                                  pdf_filename])
        if result != 0:
            raise OSError("wkhtmltopdf failed with result {0}.".format(result))

        logger.info("Sending to S3...")
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        s3_bucket = os.getenv("S3_BUCKET")
        conn = S3Connection(aws_access_key_id, aws_secret_access_key)
        try:
            bucket = conn.get_bucket(s3_bucket)
            key = Key(bucket)
            key.name = "test_{0}.pdf".format(record_pk)
            key.set_contents_from_filename(pdf_filename)
        finally:
            conn.close()

        job.result = str(result) + " " + str(os.stat(pdf_filename))
        job.end_time = now()
        job.save()

        os.unlink(html_filename)
        os.unlink(pdf_filename)
        logger.info("Created PDF at %s", pdf_filename)
        return True
    except Exception:
        logger.exception("PDF error")
        return False
