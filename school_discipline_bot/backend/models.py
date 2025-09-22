from tortoise import fields, models


class User(models.Model):
    """Abstract base user model."""
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, null=True)
    username = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255, null=True)

    class Meta:
        abstract = True


class Student(User):
    """Student model."""
    class_name = fields.CharField(max_length=10)  # e.g., "11A"
    points = fields.IntField(default=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.class_name})"


class Teacher(User):
    """Teacher model."""
    pass

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Admin(User):
    """Admin model."""
    pass

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class DisciplineRule(models.Model):
    """Discipline rule model."""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    points = fields.IntField()  # Can be positive or negative

    def __str__(self):
        return f"{self.name} ({self.points} points)"


class PointHistory(models.Model):
    """Points history model."""
    id = fields.IntField(pk=True)
    student = fields.ForeignKeyField("models.Student", related_name="point_history")
    teacher = fields.ForeignKeyField("models.Teacher", related_name="given_points")
    rule = fields.ForeignKeyField("models.DisciplineRule", related_name="applications")
    points_changed = fields.IntField()
    comment = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} got {self.points_changed} points from {self.teacher} for {self.rule}"
