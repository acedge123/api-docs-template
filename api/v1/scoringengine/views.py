import re

from rest_framework import viewsets, mixins, status, serializers
from rest_framework.response import Response

from api.v1.scoringengine.serializers import LeadSerializerCreate, LeadSerializerView
from scoringengine.models import Lead
from scoringengine.helpers import (
    add_lead_log,
    collect_answers_values,
    calculate_x_and_y_scores,
    collect_recommendations,
)


class LeadViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    API endpoint that allows lead to be created.
    """

    queryset = Lead.objects.all()

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return LeadSerializerCreate
        else:
            return LeadSerializerView

    def perform_create(self, serializer):
        answers_data = serializer.validated_data["answers"]

        provided_answers_field_names = [
            re.sub(r"\[\d+\]", "", a["field_name"]) for a in answers_data
        ]

        # Check that answers for all question provided
        for question in self.request.user.questions.all():
            if question.field_name not in provided_answers_field_names:
                raise serializers.ValidationError(
                    {"answers": ["Not all answers provided"]}
                )

        collect_answers_values(self.request.user, answers_data)

        x_axis, y_axis = calculate_x_and_y_scores(self.request.user, answers_data)
        total_score = x_axis + y_axis

        collect_recommendations(self.request.user, answers_data)

        data = {
            "owner": self.request.user,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "total_score": total_score,
            "answers": answers_data,
        }

        return serializer.save(**data)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # remove duplicate prior adding the new record
        allow_duplicates = data.pop("allow_duplicates", False)

        if allow_duplicates is True and data.get("lead_id"):
            try:
                Lead.objects.filter(lead_id__iexact=data["lead_id"]).delete()

            except:  # noqa: this part of the process is not crucial, so not worth acknowledging
                pass

        serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        add_lead_log(obj)
        headers = self.get_success_headers(serializer.data)

        view_serializer = LeadSerializerView(obj, context={"request": request})

        return Response(
            view_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
