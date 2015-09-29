import logging
import django_rq
import rq
import os
import time
import subprocess
import random
from django.template.loader import render_to_string
from tempfile import NamedTemporaryFile
from boto3.session import Session
from urllib.parse import quote


logger = logging.getLogger("django")


def generate_html(job_id):
    def create_data(n):
        import sys
        obj_type = (object, bool, tuple, float, int)
        for i in range(0, n):
            obj = random.choice(obj_type)()
            yield (i, str(obj), hash(obj), sys.getsizeof(obj))

    data = list(create_data(random.randint(25, 40)))
    html = render_to_string("pdf.html",
                            {"data": data,
                             "total": sum(x[3] for x in data),
                             "job_id": job_id})
    return html


@django_rq.job("low")
def generate_pdf(dummy_parameter):
    try:
        logger.info("Loading PDF job information...")
        rq_job = rq.get_current_job()
        wkhtmltopdf = os.path.join(os.path.expanduser("~"),
                                   "bin",
                                   "wkhtmltopdf-linux-amd64")

        logger.info("Creating HTML from template...")
        f = NamedTemporaryFile(suffix=".html", delete=False)
        html_filename = f.name
        try:
            html = generate_html(rq_job.id)
            f.write(html.encode("utf-8"))
            f.flush()
        finally:
            f.close()

        logger.info("Creating temp file for the PDF...")
        pdf_filename = None
        with NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_filename = f.name

        logger.info("Call %s...", wkhtmltopdf)
        result = subprocess.call([wkhtmltopdf, "-q", html_filename,
                                  pdf_filename])
        if result != 0:
            raise OSError("wkhtmltopdf failed with result {0}.".format(result))
        logger.info("Created PDF at %s.", pdf_filename)

        logger.info("Sending to S3...")
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        s3_bucket = os.getenv("S3_BUCKET")
        session = Session(aws_access_key_id, aws_secret_access_key)
        s3 = session.resource("s3")

        # Generate Content-Disposition metadata for the S3 file.
        s3_key_name = "test_{0}.pdf".format(int(time.time()))
        content_disposition = "attachment; filename=\"{0}\"; filename*=utf-8''{1}"
        content_disposition = content_disposition.format("test.pdf",
                                                         quote("測試 File.pdf"))
        with open(pdf_filename, "rb") as f:
            s3.Object(s3_bucket, s3_key_name).put(ACL="public-read",
                                                  ContentType="application/pdf",
                                                  ContentDisposition=content_disposition,
                                                  Body=f)

        os.unlink(html_filename)
        os.unlink(pdf_filename)
        logger.info("PDF was stored to S3 as {0}.".format(s3_key_name))
        return True
    except Exception:
        logger.exception("PDF error")
        return False
