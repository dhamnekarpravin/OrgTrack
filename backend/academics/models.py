from django.db import models

from common.models import BaseModel


class AcademicYear(BaseModel):
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = "academic_years"


class Standard(BaseModel):
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "standards"


class Division(BaseModel):
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    standard = models.ForeignKey(Standard, on_delete=models.PROTECT)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "divisions"


class Subject(BaseModel):
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    standard = models.ForeignKey(Standard, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, blank=True)
    has_theory = models.BooleanField(default=True)
    has_practical = models.BooleanField(default=False)

    class Meta:
        db_table = "subjects"


class SchoolDatabaseSetup(BaseModel):
    STATUSES = [("pending", "Pending"), ("in_progress", "In progress"), ("ready", "Ready")]

    school = models.OneToOneField("accounts.School", on_delete=models.PROTECT)
    status = models.CharField(max_length=15, choices=STATUSES, default="pending")
    configured_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    configured_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "school_database_setup"