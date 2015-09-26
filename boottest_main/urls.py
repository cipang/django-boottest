from django.conf.urls import url
from . import views


urlpatterns = [
    url(r"^add/$", views.add_records, name="add_records"),
    url(r"^showdb/$", views.show_records, name="show_records"),
    url(r"^download/$", views.download_view, name="download_view"),
    url(r"^xfile/$", views.xfile, name="xfile"),
]