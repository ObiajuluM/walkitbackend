from rest_framework import serializers
from .models import Claim, StepsPerDay, WalkUser


class WalkUserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalkUser
        fields = [
            "uuid",
            "username",
            "display_name",
            "email",
            "balance",
            "invite_code",
            "invited_by",
        ]

        read_only = [
            "uuid",
            "username",
            "display_name",
            "email",
            "balance",
            "invite_code",
            "invited_by",
        ]


class WalkUserPatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = WalkUser
        fields = [
            "display_name",
            "gender",
            # "dob",
            # "balance",
            # "invite_code",
            "invited_by",
            "dob",
            "long",
            "lat",
        ]


class WalkUserInviteSerializer(serializers.ModelSerializer):

    class Meta:
        model = WalkUser
        fields = [
            "display_name",
        ]


class StepsPerDaySerializer(serializers.ModelSerializer):
    walkuser = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),  # use the current user as param [via user]
    )

    class Meta:
        model = StepsPerDay
        fields = [
            "walkuser",
            "steps",
            "time",
        ]
        read_only = [
            "walkuser",
            "time",
        ]


# class LastSeenLocationSnapshotSerializer(serializers.ModelSerializer):
#     walkuser = serializers.HiddenField(
#         default=serializers.CurrentUserDefault(),  # use the current user as param [via user]
#     )

#     class Meta:
#         model = LastSeenLocationSnapshot
#         fields = [
#             "walkuser",
#             "latitude",
#             "longitude",
#             "time",
#         ]
#         read_only = [
#             "walkuser",
#             "time",
#         ]


class ClaimSerializer(serializers.ModelSerializer):
    walkuser = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),  # use the current user as param [via user]
    )

    class Meta:
        model = Claim
        fields = [
            "walkuser",
            "time",
            "steps_recorded",
            "steps_rewarded",
            "amount_rewarded",
            "points_per_step",
        ]
        read_only = [
            "walkuser",
            "time",
        ]
