from rest_framework import viewsets, mixins, status, serializers
from rest_framework.response import Response

from api.v1.scoringengine.serializers import LeadSerializerCreate, LeadSerializerView
from scoringengine.models import Lead


class LeadViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows lead to be created.
    """
    queryset = Lead.objects.all()

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return LeadSerializerCreate
        else:
            return LeadSerializerView

    def _calculate_answers_points(self, answers_data):
        """  Calculate answer points for questions that have choices

        Answer points = choice points * question weight
        """

        for answer_data in answers_data:
            question = self.request.user.questions.filter(field_name=answer_data['field_name']).first()

            if question is None:
                raise serializers.ValidationError({
                    'answers': {'field_name': [f"There are no question with '{answer_data['field_name']}' field name"]}
                })

            choice = question.choices.filter(slug=answer_data['response']).first()

            if choice is None:
                if question.choices.count() > 0:
                    raise serializers.ValidationError({
                        'answers': {
                            'response': [f"There are no question choice with '{answer_data['response']}' response"]
                        }
                    })
            else:
                answer_data['points'] = choice.points * question.weight
                answer_data['value'] = choice.value

    def _calculate_x_and_y_scores(self, answers_data):
        """ Calculate X-axis and Y-axis scores """

        x_axis = 0
        y_axis = 0

        for answer_data in answers_data:
            question = self.request.user.questions.filter(field_name=answer_data['field_name']).first()

            points = answer_data.get('points')

            if points is not None:
                if question.x_axis:
                    x_axis += points

                if question.y_axis:
                    y_axis += points

        return x_axis, y_axis

    def _collect_recommendations(self, answers_data):
        """  Collect recommendations by checking each question rule against provided answers """

        answers = {a['field_name']: a['value'] for a in answers_data if a.get('value') is not None}

        for answer_data in answers_data:
            question = self.request.user.questions.filter(field_name=answer_data['field_name']).first()

            if question.check_rule(answers):
                answer_data.update(question.get_recommendation_dict())

    def perform_create(self, serializer):
        answers_data = serializer.validated_data['answers']

        provided_answers_field_names = [a['field_name'] for a in answers_data]

        # Check that answers for all question provided
        for question in self.request.user.questions.all():
            if question.field_name not in provided_answers_field_names:
                raise serializers.ValidationError({
                    'answers': ['Not all answers provided']
                })

        self._calculate_answers_points(answers_data)

        x_axis, y_axis = self._calculate_x_and_y_scores(answers_data)

        self._collect_recommendations(answers_data)

        data = {
            'owner': self.request.user,
            'x_axis': x_axis,
            'y_axis': y_axis,
            'answers': answers_data
        }

        return serializer.save(**data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        view_serializer = LeadSerializerView(obj, context={'request': request})

        return Response(view_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
