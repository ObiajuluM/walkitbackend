import hashlib
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# pip install unique-namer
import namer


# Create your models here.


class WalkUser(AbstractUser):
    # uid = models.TextField(
    #     db_index=True,
    #     unique=True,
    # )
    uuid = models.UUIDField(
        "UUID",  # name of the field with transaltion support
        default=uuid.uuid4,  # default field for the uuid
        unique=True,  # make unique
        editable=False,  #  make not editable
        db_index=True,  # set to be used as db index - query by uuid
    )
    username = models.CharField("username", max_length=255)

    display_name = models.CharField(
        "display_name",
        max_length=255,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        "email",
        unique=True,
        db_index=True,  # set to be used as db index - query by uuid
    )
    gender = models.CharField(
        "gender",
        null=True,
        blank=True,
        max_length=100,
    )

    dob = models.DateField(
        "dob",
        null=True,
        blank=True,
    )
    balance = models.FloatField("balance", default=0)
    invite_code = models.CharField(
        "invite_code",
        max_length=20,
        unique=True,  # make unique
        editable=False,
        null=True,
        blank=True,
    )
    invited_by = models.CharField(
        "invited_by",
        max_length=255,
        null=True,
        blank=True,
    )
    long = models.DecimalField(
        "long",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    lat = models.DecimalField(
        "lat",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    # string representation of the model
    def __str__(self) -> str:
        return self.username

    def __generate_invite_code(self, data: str) -> str:
        """method to generate invite code"""
        sha256 = hashlib.sha256()
        sha256.update(data.encode("utf-8"))
        return sha256.hexdigest()[:8]

    def __generate_display_name(self) -> str:
        """method to generate display name"""
        return namer.generate(
            separator=" ",
            style="title",
        )

    def save(self, **kwargs):
        if not self.invite_code:  # generate invite code if its empty
            self.invite_code = self.__generate_invite_code(self.email)
        if not self.display_name:  # generate display name if its empty
            self.display_name = self.__generate_display_name()
        return super().save(**kwargs)  # Call the "real" save() method.


class StepsPerDay(models.Model):
    walkuser = models.OneToOneField(
        WalkUser,
        verbose_name="walkuser",
        related_name="steps_per_day",
        on_delete=models.CASCADE,
    )
    steps = models.PositiveIntegerField("steps", null=True, blank=True)
    time = models.DateTimeField("time", auto_now=True)

    # class Meta:
    #     # set to sort the models in the databse by the newest first
    #     ordering = ["-time"]

    def __str__(self) -> str:
        return f"{self.walkuser.username} steps for {self.time.strftime('%d/%m/%Y')}"


class Claim(models.Model):
    walkuser = models.ForeignKey(
        WalkUser,
        verbose_name="walkuser",
        related_name="claims",
        on_delete=models.CASCADE,
    )
    time = models.DateTimeField("time", auto_now_add=True)
    steps_recorded = models.PositiveIntegerField(
        "steps_recorded",
        null=True,
        blank=True,
    )
    steps_rewarded = models.PositiveIntegerField(
        "steps_rewarded",
        null=True,
        blank=True,
    )
    amount_rewarded = models.FloatField(
        "amount_rewarded",
        null=True,
        blank=True,
    )
    points_per_step = models.FloatField(
        "points_per_step",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.walkuser.username} claim on {self.time.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        # set to sort the models in the databse by the newest first
        ordering = ["-time"]
