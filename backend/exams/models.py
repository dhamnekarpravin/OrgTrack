from django.db import models

from common.models import BaseModel, SoftDeleteModel


class ExamType(BaseModel):
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    weightage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = "exam_types"


class Exam(BaseModel):
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.PROTECT)
    exam_type = models.ForeignKey(ExamType, on_delete=models.PROTECT)
    standard = models.ForeignKey("academics.Standard", on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "exams"


class GradingScale(BaseModel):
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    grade = models.CharField(max_length=10)
    min_percent = models.DecimalField(max_digits=5, decimal_places=2)
    max_percent = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "grading_scales"


class StudentMark(SoftDeleteModel):
    COMPONENTS = [("theory", "Theory"), ("practical", "Practical")]

    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    student = models.ForeignKey("people.Student", on_delete=models.PROTECT)
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT)
    subject = models.ForeignKey("academics.Subject", on_delete=models.PROTECT)
    component = models.CharField(max_length=10, choices=COMPONENTS)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    grade = models.CharField(max_length=10, blank=True)
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")

    class Meta:
        db_table = "student_marks"
        unique_together = [("student", "exam", "subject", "component")]


class StudentProgress(BaseModel):
    COMPONENTS = [("theory", "Theory"), ("practical", "Practical"), ("overall", "Overall")]

    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    student = models.ForeignKey("people.Student", on_delete=models.PROTECT)
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.PROTECT)
    subject = models.ForeignKey(
        "academics.Subject", null=True, blank=True, on_delete=models.PROTECT
    )
    component = models.CharField(max_length=10, choices=COMPONENTS, default="overall")
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=10, blank=True)
    calculated_at = models.DateTimeField()

    class Meta:
        db_table = "student_progress"


class LeaderboardEntry(BaseModel):
    SCOPES = [
        ("division", "Division"),
        ("standard", "Standard"),
        ("subject", "Subject"),
        ("theory", "Theory"),
        ("practical", "Practical"),
    ]

    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.PROTECT)
    scope_type = models.CharField(max_length=10, choices=SCOPES)
    division = models.ForeignKey(
        "academics.Division", null=True, blank=True, on_delete=models.PROTECT
    )
    standard = models.ForeignKey(
        "academics.Standard", null=True, blank=True, on_delete=models.PROTECT
    )
    subject = models.ForeignKey(
        "academics.Subject", null=True, blank=True, on_delete=models.PROTECT
    )
    student = models.ForeignKey("people.Student", on_delete=models.PROTECT)
    score = models.DecimalField(max_digits=6, decimal_places=2)
    rank_position = models.PositiveIntegerField()
    calculated_at = models.DateTimeField()

    class Meta:
        db_table = "leaderboard_entries"