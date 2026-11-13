"""URL routes for board endpoints.

The detail route accepts an optional trailing slash because the frontend
requests ``boards/<id>`` without one; a redirect would break CORS preflight.
"""

from django.urls import path, re_path

from .views import BoardDetailView, BoardListCreateView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list'),
    re_path(
        r'^boards/(?P<pk>\d+)/?$',
        BoardDetailView.as_view(),
        name='board-detail',
    ),
]