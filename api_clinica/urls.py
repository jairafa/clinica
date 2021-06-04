from django.conf.urls import url, include
from django.contrib import admin

from api.users.views import Login, Logout, UserToken

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls', namespace="api")),
]

"""
    url(r'^login/', Login.as_view(), name='login'),
    url(r'^logout/', Logout.as_view(), name='logout'),
    url(r'^refresh-token/',UserToken.as_view(), name = 'refresh_token'),
"""
