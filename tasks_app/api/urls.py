"""URL routes for task and comment endpoints."""

from django.urls import path

from .views import (
    AssignedTaskListView,
    CommentDeleteView,
    CommentListCreateView,
    ReviewingTaskListView,
    TaskCreateView,
    TaskDetailView,
)

urlpatterns = [
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path(
        'tasks/assigned-to-me/',
        AssignedTaskListView.as_view(),
        name='tasks-assigned',
    ),
    path(
        'tasks/reviewing/',
        ReviewingTaskListView.as_view(),
        name='tasks-reviewing',
    ),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path(
        'tasks/<int:task_id>/comments/',
        CommentListCreateView.as_view(),
        name='comment-list',
    ),
    path(
        'tasks/<int:task_id>/comments/<int:comment_id>/',
        CommentDeleteView.as_view(),
        name='comment-detail',
    ),
]
