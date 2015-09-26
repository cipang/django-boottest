import logging
import math
import random
from django.shortcuts import render
from django.utils.timezone import now
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from .models import TestRecord


_CHARS = "AacdEeFfGHhiJKLmNnpQRrsTtwxYy12346789"


def _random_str(n=5):
    return "".join([random.choice(_CHARS) for i in range(0, n)])


def _repeat_and_wait(obj, repeat, ops_between_iteration):
    for i in range(0, repeat):
        r = 0.0
        for j in range(0, ops_between_iteration):
            r += (1 if bool(random.randint(0, 1)) else -1) * random.random()
        yield obj


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
        logging.info("mb=-1 passed in.")
        print(math.sqrt(-1))

    buffer1k = _random_str(1023) + "/"
    mb = max(int(request.POST["mb"]), 1)
    ops = int(request.POST.get("ops", 0))
    logging.info("Start generating %dMB data now (with ops=%d)...", mb, ops)
    response = StreamingHttpResponse()
    response["Content-Type"] = "application/binary"
    response["Content-Disposition"] = "attachment; filename=\"random{0}-{1}MB.bin\"".format(random.randint(10, 99), mb)
    response["Content-Length"] = str(1024 * 1024 * mb)
    response.streaming_content = _repeat_and_wait(buffer1k, 1024 * mb, ops)
    logging.info("Passing the generator to the response.")
    return response


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
