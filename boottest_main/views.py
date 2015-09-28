import logging
import math
import random
import django_rq
import time
import traceback
from django.shortcuts import render
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from .models import TestRecord, BackgroundJob


_CHARS = "AacdEeFfGHhiJKLmNnpQRrsTtwxYy12346789"
_LOG = logging.getLogger("django")


def _random_str(n=5):
    return "".join([random.choice(_CHARS) for i in range(0, n)])


def _repeat_and_wait(obj, repeat, ops_between_iteration):
    for i in range(0, repeat):
        r = 0.0
        for j in range(0, ops_between_iteration):
            r += (1 if bool(random.randint(0, 1)) else -1) * random.random()
        yield obj


def _long_operation(job_name, x, sec):
    _LOG.info("{0}: x={1} sec={2}".format(job_name, x, sec))
    record = BackgroundJob.objects.get(id=x)
    try:
        result = int(record.args) ** 2
        time.sleep(sec)
        record.result = str(result)
        record.end_time = now()
        record.save()
        _LOG.info("{0}: Done, result={1}".format(job_name, result))
        return result
    except Exception:
        record.error = traceback.format_exc()
        record.save()
        _LOG.exception("Cannot perform operation for x=%s.", x)


@django_rq.job("high")
def _long_high_job(x):
    return _long_operation("HIGH" + str(random.randint(1, 999)), x, 10)


@django_rq.job("low")
def _long_low_job(x):
    return _long_operation("LOW" + str(random.randint(1, 999)), x, 5)


def home(request):
    return render(request, "home.html", {"now": now(), "filename": __file__})


def add_records(request):
    n = int(request.GET.get("n", 100))
    for i in range(0, n):
        r = TestRecord()
        r.num_value = random.random() * 500
        r.text_value = _random_str(10)
        r.created = now()
        r.save(force_insert=True)
    return HttpResponse("Created " + str(n) + " database record(s).")


def show_records(request):
    qs = TestRecord.objects.all()
    return render(request, "db.html", {"data": qs})


def download_view(request):
    if request.method == "GET":
        return render(request, "download.html")

    if request.POST["mb"] == "-1":
        # Intentionally generate an exception.
        _LOG.info("mb=-1 passed in.")
        print(math.sqrt(-1))

    buffer1k = _random_str(1023) + "/"
    mb = max(int(request.POST["mb"]), 1)
    ops = int(request.POST.get("ops", 0))
    _LOG.info("Start generating %dMB data now (with ops=%d)...", mb, ops)
    response = StreamingHttpResponse()
    response["Content-Type"] = "application/binary"
    response["Content-Disposition"] = "attachment; filename=\"random{0}-{1}MB.bin\"".format(random.randint(10, 99), mb)
    response["Content-Length"] = str(1024 * 1024 * mb)
    response.streaming_content = _repeat_and_wait(buffer1k, 1024 * mb, ops)
    logging.info("Passing the generator to the response.")
    return response


def queue_view(request):
    if request.method == "GET":
        return render(request, "queue.html")

    x = random.randint(1, 100)
    job_type = ""
    job = None
    func = None

    if request.POST.get("high"):
        func = _long_high_job
        job_type = "high"
    elif request.POST.get("low"):
        func = _long_low_job
        job_type = "low"
    elif request.POST.get("pdf"):
        from .htmltopdf import generate_pdf
        func = generate_pdf
        job_type = "pdf"
    else:
        func = _long_low_job
        x = None
        job_type = "fail"

    r = BackgroundJob.objects.create(method=job_type,
                                     args=str(x),
                                     start_time=now())
    _LOG.info("Created a record for job, pk=%d", r.id)

    job = func.delay(r.id)
    r.job_id = job.id
    r.save()
    _LOG.info("Queued RQ job with ID %s", job.id)

    return render(request, "queue.html",
                  {"msg": "Queued a {0} job.".format(job_type),
                   "now": now()})


def xfile(request):
    if request.method == "GET":
        return render(request, "xfile.html")

    filename = request.POST["filename"]
    if not filename:
        return HttpResponse("No filename provided.", content_type="text/plain")

    file_path = settings.MEDIA_URL + filename
    response = HttpResponse(content_type="application/octet-stream")
    response["X-Accel-Redirect"] = file_path
    response["Content-Disposition"] = 'attachment; filename="' + filename + '"'
    return response


def test_pdf(request):
    html = render_to_string("pdf.html",
                            {"data": TestRecord.objects.all()[0:20],
                             "job_id": "No Job ID - Testing"})
    return HttpResponse(html)
