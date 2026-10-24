from django.db import models

from common.models import BaseModel, SoftDeleteModel


class Announcement(SoftDeleteModel):
    AUDIENCES = [
        ("all", "All"),
        ("teachers", "Teachers"),
        ("students", "Students"),
        ("parents", "Parents"),
    ]

    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    body = models.TextField()
    audience = models.CharField(max_length=10, choices=AUDIENCES, default="all")
    posted_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "announcements"


class EventRequest(BaseModel):
    TYPES = [
        ("festival", "Festival"),
        ("hackathon", "Hackathon"),
        ("sports", "Sports"),
        ("other", "Other"),
    ]
    STATUSES = [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")]

    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    event_type = models.CharField(max_length=10, choices=TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    venue = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    requested_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    status = models.CharField(max_length=10, choices=STATUSES, default="pending")
    decided_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    decision_note = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "event_requests"


class HelpdeskTicket(BaseModel):
    CATEGORIES = [
        ("account_blocked", "Account blocked"),
        ("access_issue", "Access issue"),
        ("other", "Other"),
    ]
    PRIORITIES = [("low", "Low"), ("medium", "Medium"), ("high", "High")]
    STATUSES = [
        ("open", "Open"),
        ("in_progress", "In progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    raised_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    category = models.CharField(max_length=20, choices=CATEGORIES, default="other")
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITIES, default="medium")
    status = models.CharField(max_length=15, choices=STATUSES, default="open")
    assigned_to = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    resolved_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "helpdesk_tickets"


class TicketComment(BaseModel):
    ticket = models.ForeignKey(HelpdeskTicket, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    message = models.TextField()

    class Meta:
        db_table = "ticket_comments"


class MeetingRequest(BaseModel):
    STATUSES = [
        ("requested", "Requested"),
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("declined", "Declined"),
    ]

    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    parent = models.ForeignKey("people.Parent", on_delete=models.PROTECT)
    student = models.ForeignKey("people.Student", on_delete=models.PROTECT)
    reason = models.TextField()
    preferred_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default="requested")
    handled_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "meeting_requests"