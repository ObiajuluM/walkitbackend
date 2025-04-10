from rest_framework import response
from rest_framework import generics, status
from rest_framework import permissions

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from backend.web3_methods import NETWORKS_LIST_, on_chain


from .constants import (
    MAX_STEP_TO_REWARD,
    MIN_STEP_TO_REWARD,
    POINT_PER_STEP,
    REWARD_FOR_INVITED,
    REWARD_FOR_INVITING,
)
from .permissions import IsOwner
from django.utils import timezone

from backend.models import Claim, StepsPerDay, WalkUser
from backend.serializers import (
    ClaimSerializer,
    StepsPerDaySerializer,
    WalkUserInviteSerializer,
    WalkUserMeSerializer,
    WalkUserPatchSerializer,
)

# Authentication: Ensure that the user is authenticated before accessing this viewset.
# Permissions: Implement appropriate permissions to control who can access the user's posts.
# Pagination: Consider using pagination to optimize performance for large datasets.
# Caching

# Create your views here.


class WalkUserView(
    generics.UpdateAPIView,
    generics.RetrieveAPIView,
):
    queryset = WalkUser.objects.all()
    serializer_class = WalkUserPatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    # show only methods in here
    http_method_names = ["patch", "get"]
    # lookup_field = "email"

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = WalkUserMeSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [
                IsOwner,
                permissions.IsAuthenticated,
            ]
        return super().get_permissions()

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            print("obi is cool")
            return response.Response(
                data=WalkUserMeSerializer(
                    WalkUser.objects.get(email=self.request.user.email),
                    many=False,
                ).data,
                status=status.HTTP_200_OK,
            )
            # return super().retrieve(request, *args, **kwargs)

    def __get_invited__update_my_balance__update_inviter_balance__add_claim_for_both_parties(
        self,
        invited_by_code: str,
        walkuserme: WalkUser,
    ):
        try:
            walkuserinviter = WalkUser.objects.get(invite_code=invited_by_code)

        except WalkUser.DoesNotExist:
            return response.Response(
                data={"error": "user doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )

        # walkuserme = WalkUser.objects.get(email=email)

        # if my invited by string is empty and i am not trying to invite myself
        if (
            #  i changed here
            walkuserme.invited_by is None
            or walkuserme.invited_by == ""
            and walkuserinviter.email != walkuserme.email
        ):
            # update my status as already invited with xxx code
            walkuserme.invited_by = walkuserinviter.display_name
            # update my balance
            walkuserme.balance = walkuserme.balance + REWARD_FOR_INVITED
            # add claim
            walkuserme_newclaim = Claim.objects.create(
                walkuser=walkuserme,
                amount_rewarded=REWARD_FOR_INVITED,
            )
            walkuserme.save()
            walkuserme_newclaim.save()

            # update inviters balance
            walkuserinviter.balance = walkuserinviter.balance + REWARD_FOR_INVITING
            # add claim
            walkuserinviter_newclaim = Claim.objects.create(
                walkuser=walkuserinviter,
                amount_rewarded=REWARD_FOR_INVITING,
            )
            print(walkuserinviter.display_name)
            walkuserinviter.save()
            walkuserinviter_newclaim.save()

            return response.Response(
                {"result": f"invited by {walkuserinviter.display_name}"},
                status=status.HTTP_200_OK,
            )

    def patch(self, request, *args, **kwargs):
        # if user is authenticated

        try:
            walkuserme = WalkUser.objects.get(email=self.request.user.email)
        except WalkUser.DoesNotExist:
            return response.Response(
                data={"error": "user doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )

        if self.request.user.is_authenticated:
            if "invited_by" in request.data:
                print("entered here!")
                print(request.data["invited_by"])

                return self.__get_invited__update_my_balance__update_inviter_balance__add_claim_for_both_parties(
                    invited_by_code=request.data["invited_by"],
                    walkuserme=walkuserme,
                )
            else:
                # if self.request.user.is_authenticated:
                #     if isinstance(kwargs.get("invited_by"), str) == False:
                print("dont here!")
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                # walkuser = WalkUser.objects.get(email=self.request.user.email)
                for field, value in serializer.validated_data.items():
                    setattr(walkuserme, field, value)
                walkuserme.save()
                return response.Response(
                    serializer.data,
                    status=status.HTTP_200_OK,
                )


def add_balance__add_claim(steps: int, walkuserme: WalkUser):
    if steps < MIN_STEP_TO_REWARD:
        # add the steps to the blockchain
        for networks in NETWORKS_LIST_:
            try:
                # call the on chain function somnia
                on_chain(
                    network_url=networks["url"],
                    contract_address=networks["contract"],
                    user_id=f"{walkuserme.display_name}",
                    step_count=steps,
                )
            except Exception as e:
                print(e)
        return

    steps_to_reward = steps
    # if the steps you got are bigger than the max steps we reward set it to the max steps we reward
    if steps_to_reward > MAX_STEP_TO_REWARD:
        steps_to_reward = MAX_STEP_TO_REWARD
    # get me
    # walkuserme = WalkUser.objects.get(email=email)
    # add balance
    calculate = steps_to_reward * POINT_PER_STEP
    walkuserme.balance = walkuserme.balance + calculate

    # create claim
    new_claim = Claim.objects.create(
        walkuser=walkuserme,
        steps_recorded=steps,
        steps_rewarded=steps_to_reward,
        amount_rewarded=calculate,
        points_per_step=POINT_PER_STEP,
    )

    new_claim.save()
    walkuserme.save()

    # add the steps to the blockchain
    for networks in NETWORKS_LIST_:
        try:
            # call the on chain function somnia
            on_chain(
                network_url=networks["url"],
                contract_address=networks["contract"],
                user_id=f"{walkuserme.display_name}",
                step_count=steps,
            )
        except Exception as e:
            print(e)


# modify your steps for the day
class ListCreateStepsPerDayView(
    generics.CreateAPIView,
    generics.RetrieveUpdateAPIView,
    generics.ListCreateAPIView,
):
    queryset = StepsPerDay.objects.all()
    serializer_class = StepsPerDaySerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    http_method_names = ["get", "post", "put"]

    # def get_serializer_class(self):
    #     if self.request.method == "GET":
    #         self.serializer_class =
    #     return super().get_serializer_class()

    # def get_permissions(self):
    #     return super().get_permissions()

    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            try:

                walkuser = WalkUser.objects.get(email=self.request.user.email)
                user_steps_per_day = StepsPerDay.objects.get(walkuser=walkuser)

                # stepn = serializer.validated_data.get("steps")
                stepn = int(self.request.data.get("steps"))

                user_steps_per_day.steps = stepn
                user_steps_per_day.save()

                # TODO: if StepsPerDay.objects.time == today : pass
                if (
                    user_steps_per_day.time.month == timezone.now().month
                    and user_steps_per_day.time.day == timezone.now().day
                ):
                    return response.Response(
                        data={
                            "steps": user_steps_per_day.steps,
                            "time": user_steps_per_day.time,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    # show love
                    add_balance__add_claim(steps=stepn, walkuserme=walkuser)

                return response.Response(
                    data={
                        "steps": user_steps_per_day.steps,
                        "time": user_steps_per_day.time,
                    },
                    status=status.HTTP_200_OK,
                )
            # use this if this if step per day == null
            except StepsPerDay.DoesNotExist:
                stepn = int(self.request.data.get("steps"))
                walkuser = WalkUser.objects.get(email=self.request.user.email)
                StepsPerDay.objects.create(walkuser=walkuser, steps=stepn)
                # walkuser = WalkUser.objects.get(email=self.request.user.email)
                user_steps_per_day = StepsPerDay.objects.get(walkuser=walkuser)

                # call the show love function
                add_balance__add_claim(steps=stepn, walkuserme=walkuser)

                return response.Response(
                    data={
                        "steps": user_steps_per_day.steps,
                        "time": user_steps_per_day.time,
                    },
                    status=status.HTTP_200_OK,
                )

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:

            users_with_steps = []
            #  sort top steps
            top_steps = StepsPerDay.objects.filter(
                time__date=timezone.now().date() - timezone.timedelta(days=1),
                steps__gt=MIN_STEP_TO_REWARD,
            ).order_by("-steps")[:100]

            # today = timezone.now().date()
            # return StepsPerDay.objects.filter(
            #     modified_date__date=today,
            #     steps__gt=100
            # ).order_by('-steps')[:100]

            # Fetch user for each StepsPerDay object
            for top_step in top_steps:
                top_user = {}
                top_user["display_name"] = (
                    top_step.walkuser.display_name
                )  # Assuming you have a User model
                top_user["steps"] = top_step.steps
                top_user["time"] = top_step.time
                users_with_steps.append(top_user)

            # print(users_with_steps)

            return response.Response(
                # data=self.serializer_class(top_steps).data,
                data={"data": users_with_steps},
                status=status.HTTP_200_OK,
            )


class ClaimView(generics.ListAPIView):
    """return all your claims"""

    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        # email = self.kwargs["email"]
        if self.request.user.is_authenticated:
            walkuser = WalkUser.objects.get(email=self.request.user.email)
            return Claim.objects.filter(walkuser=walkuser).order_by("time")


class InviteView(generics.ListAPIView):
    """View to return all your invites"""

    queryset = WalkUser.objects.all()
    serializer_class = WalkUserInviteSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    # http_method_names = ["get", "post", "put"]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            walkuser = WalkUser.objects.get(email=self.request.user.email)
            return WalkUser.objects.filter(invited_by=walkuser.display_name)


#  return the user's steps for today
class UserStepsPerDayView(
    generics.RetrieveAPIView,
):
    queryset = StepsPerDay.objects.all()
    serializer_class = StepsPerDaySerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    # show only methods in here
    # http_method_names = [
    #     # "post",
    #     "get",
    # ]
    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request):
        if self.request.user.is_authenticated:
            walkuser = WalkUser.objects.get(email=self.request.user.email)
            # return StepsPerDay.objects.filter(walkuser=walkuser)
            walkuserstep = StepsPerDaySerializer(
                StepsPerDay.objects.filter(walkuser=walkuser).get(), many=False
            ).data
            return response.Response(
                walkuserstep,
                status=status.HTTP_200_OK,
            )
            # response.Response(
            #     StepsPerDaySerializer(
            #         StepsPerDay.objects.filter(walkuser=walkuser)
            #     ).data
            # )

    # def get(self, request, email, *args, **kwargs):
    #     user = WalkUser.objects.get(email=email)
    #     steps = StepsPerDay.objects.filter(walkuser=user).get()
    #     usersteps = self.serializer_class(steps, many=False)
    #     return response.Response(
    #         data=usersteps.data, status=rest_framework.status.HTTP_200_OK
    #     )
