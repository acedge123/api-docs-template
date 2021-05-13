from rest_framework import viewsets, mixins, status, serializers
from rest_framework.response import Response

from api.v1.core.permissions import IsOwner
from api.v1.scoringengine.serializers import QuestionSerializer, LeadSerializerCreate, LeadSerializerView
from scoringengine.models import Question, Lead


class QuestionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner=self.request.user)


class LeadViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows lead to be created.
    """
    queryset = Lead.objects.all()
    permission_classes = (IsOwner,)

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return LeadSerializerCreate
        else:
            return LeadSerializerView

    def perform_create(self, serializer):
        answers = {a['field_name']: a['response'] for a in serializer.validated_data['answers']}

        # Check that answers for all question provided
        for question in self.request.user.questions.all():
            if question.field_name not in answers:
                raise serializers.ValidationError({
                    'answers': ['Not all answers provided']
                })

        # Calculate answer points and collect recommendations
        answers_data = []
        for field_name, response in answers.items():
            question = self.request.user.questions.filter(field_name=field_name).first()

            if question is None:
                raise serializers.ValidationError({
                    'answers': {'field_name': [f"There are no question with '{field_name}' field name"]}
                })

            choice = question.choices.filter(text=response).first()

            if choice is None:
                raise serializers.ValidationError({
                    'answers': {'response': [f"There are no question choice with '{response}' response"]}
                })

            answer_data = {
                'field_name': field_name,
                'response': response,
                'points': choice.points * question.weight,
            }

            if question.check_rule(answers):
                answer_data.update(question.get_recommendation_dict())

            answers_data.append(answer_data)

        # Calculate X-axis and Y-axis scores
        answers = {a['field_name']: a['points'] for a in answers_data}

        x_axis = 0
        y_axis = 0
        for question in self.request.user.questions.all():
            points = answers[question.field_name]

            if question.x_axis:
                x_axis += points

            if question.y_axis:
                y_axis += points

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

        view_serializer = LeadSerializerView(obj)

        return Response(view_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
