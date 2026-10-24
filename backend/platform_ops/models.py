from django.db import models
from django.utils import timezone

from common.models import BaseModel


class RevenueRecord(BaseModel):
    STATUSES = [("due", "Due"), ("paid", "Paid"), ("overdue", "Overdue")]

    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    period_start = models.DateField()
    period_end = models.DateField()
    paid_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default="due")

    class Meta:
        db_table = "revenue_records"


class SystemCost(BaseModel):
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    incurred_on = models.DateField()
    description = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        db_table = "system_costs"


class Report(BaseModel):
    TYPES = [
        ("profit", "Profit"),
        ("revenue", "Revenue"),
        ("loss", "Loss"),
        ("other", "Other"),
    ]

    report_type = models.CharField(max_length=10, choices=TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    generated_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    result = models.JSONField(default=dict)
    generated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "reports"


class SystemMetric(BaseModel):
    metric_name = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "system_metrics"


class SystemIssue(BaseModel):
    SEVERITIES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]
    STATUSES = [("open", "Open"), ("in_progress", "In progress"), ("resolved", "Resolved")]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITIES, default="medium")
    status = models.CharField(max_length=15, choices=STATUSES, default="open")
    reported_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    assigned_to = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "system_issues"


class MarketingPromotion(BaseModel):
    STATUSES = [("planned", "Planned"), ("active", "Active"), ("ended", "Ended")]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    channel = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default="planned")
    created_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        db_table = "marketing_promotions"