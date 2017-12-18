from __future__ import unicode_literals


class WorkflowException(Exception):
    """Base exception for the document states app"""


class WorkflowStateActionError(WorkflowException):
    """Raise for errors during exection of workflow state actions"""
