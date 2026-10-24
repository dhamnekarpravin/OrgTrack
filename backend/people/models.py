from django.db import models

from common.models import BaseModel, SoftDeleteModel


class Teacher(SoftDeleteModel):
    user = models.OneToOneField(
        "accounts.User", on_delete=models.PROTECT, related_name="teacher_profile"
    )
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    employee_code = models.CharField(max_length=30, blank=True)
    department = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=150, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "teachers"


class Parent(SoftDeleteModel):
    user = models.OneToOneField(
        "accounts.User", on_delete=models.PROTECT, related_name="parent_profile"
    )
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    occupation = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "parents"


class Student(SoftDeleteModel):
    STATUSES = [("active", "Active"), ("alumni", "Alumni"), ("left", "Left")]
    GENDERS = [("male", "Male"), ("female", "Female"), ("other", "Other")]

    user = models.OneToOneField(
        "accounts.User", on_delete=models.PROTECT, related_name="student_profile"
    )
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    admission_no = models.CharField(max_length=30)
    roll_no = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDERS, blank=True)
    standard = models.ForeignKey("academics.Standard", on_delete=models.PROTECT)
    division = models.ForeignKey("academics.Division", on_delete=models.PROTECT)
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.PROTECT)
    admission_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default="active")
    parents = models.ManyToManyField(
        Parent, through="StudentParent", through_fields=("student", "parent"), related_name="children"
    )

    class Meta:
        db_table = "students"
        unique_together = [("school", "admission_no")]


class StudentParent(models.Model):
    RELATIONS = [("father", "Father"), ("mother", "Mother"), ("guardian", "Guardian")]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    relation = models.CharField(max_length=10, choices=RELATIONS)

    class Meta:
        db_table = "student_parents"
        unique_together = [("student", "parent")]


class TeacherAssignment(BaseModel):
    school = models.ForeignKey("accounts.School", on_delete=models.PROTECT)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT)
    division = models.ForeignKey("academics.Division", on_delete=models.PROTECT)
    subject = models.ForeignKey("academics.Subject", on_delete=models.PROTECT)
    academic_year = models.ForeignKey("academics.AcademicYear", on_delete=models.PROTECT)

    class Meta:
        db_table = "teacher_assignments"