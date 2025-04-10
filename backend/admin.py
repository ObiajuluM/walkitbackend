from django.contrib import admin

from backend.models import (
    Claim,
    # LastSeenLocationSnapshot,
    StepsPerDay,
    WalkUser,
)


class ClaimInline(admin.TabularInline):
    model = Claim
    extra = 0


# Register your models here.
@admin.register(WalkUser)
class WalkUserAdmin(admin.ModelAdmin):
    #  configure stuff about admin

    # fields you wanted to be searched
    search_fields = ["email", "name"]

    # force readonly fields - make fields unchangeable*
    readonly_fields = [
        # "uid",
        "uuid",
        "steps_per_day",
        # "last_seen_location",
        # "claims",
    ]
    inlines = [ClaimInline]

    # fieldsets = (
    #     (
    #         "Misc Info",
    #         {"fields": ["steps_per_day", "last_seen_location", "claims"]},
    #     ),
    # )


# @admin.register(LastSeenLocationSnapshot)
# class LastSeenLocationSnapshotAdmin(admin.ModelAdmin):
#     readonly_fields = ["time"]


@admin.register(StepsPerDay)
class StepsPerDayAdmin(admin.ModelAdmin):
    readonly_fields = ["time"]


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    # readonly_fields = ["time"]
    pass
