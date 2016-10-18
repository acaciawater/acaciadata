from django.conf.urls import url

urlpatterns = [
    url(r'^find', 'acacia.data.knmi.views.find_stations', name='find_stations'),
    url(r'^select', 'acacia.data.knmi.views.select_station', name='select_station'),
]
