import re

from rest_framework import viewsets, mixins, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Count, Avg, Q

from api.v1.scoringengine.serializers import (
    LeadSerializerCreate, 
    LeadSerializerView,
    QuestionSerializer,
    ChoiceSerializer,
    ScoringModelSerializer,
    ValueRangeSerializer,
    DatesRangeSerializer,
    RecommendationSerializer,
    UserSerializer,
    LeadAnalyticsSerializer
)
from scoringengine.models import (
    Lead, Question, Choice, ScoringModel, ValueRange, 
    DatesRange, Recommendation
)
from scoringengine.helpers import (
    add_lead_log,
    collect_answers_values,
    calculate_x_and_y_scores,
    collect_recommendations,
)
from users.models import User


class LeadViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    API endpoint for lead management.
    
    Provides endpoints to create and retrieve leads with automatic scoring.
    Requires authentication via token.
    """

    queryset = Lead.objects.all()
    permission_classes = [IsAuthenticated]

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
        """
        Create a new lead with automatic scoring.
        
        Accepts lead data with answers and automatically calculates X/Y axis scores
        and total score based on the user's scoring model.
        
        Parameters:
        - answers: List of answer objects with field_name and response
        - allow_duplicates: Boolean to allow duplicate lead_id (optional)
        - lead_id: Unique identifier for the lead (optional)
        """
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


class QuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing questions.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(owner=self.request.user).order_by('number')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def choices(self, request, pk=None):
        """Get choices for a specific question"""
        question = self.get_object()
        choices = question.choices.all()
        serializer = ChoiceSerializer(choices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def scoring_model(self, request, pk=None):
        """Get scoring model for a specific question"""
        question = self.get_object()
        try:
            scoring_model = question.scoring_model
            serializer = ScoringModelSerializer(scoring_model)
            return Response(serializer.data)
        except ScoringModel.DoesNotExist:
            return Response({'detail': 'No scoring model found'}, status=404)

    @action(detail=True, methods=['get'])
    def recommendation(self, request, pk=None):
        """Get recommendation for a specific question"""
        question = self.get_object()
        try:
            recommendation = question.recommendation
            serializer = RecommendationSerializer(recommendation)
            return Response(serializer.data)
        except Recommendation.DoesNotExist:
            return Response({'detail': 'No recommendation found'}, status=404)


class ChoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing choices.
    """
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Choice.objects.filter(question__owner=self.request.user)

    def perform_create(self, serializer):
        question_id = self.request.data.get('question')
        question = Question.objects.get(id=question_id, owner=self.request.user)
        serializer.save(question=question)


class ScoringModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing scoring models.
    """
    serializer_class = ScoringModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScoringModel.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        question_id = self.request.data.get('question')
        question = Question.objects.get(id=question_id, owner=self.request.user)
        serializer.save(owner=self.request.user, question=question)

    @action(detail=True, methods=['get'])
    def value_ranges(self, request, pk=None):
        """Get value ranges for a specific scoring model"""
        scoring_model = self.get_object()
        value_ranges = scoring_model.ranges.all()
        serializer = ValueRangeSerializer(value_ranges, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def dates_ranges(self, request, pk=None):
        """Get date ranges for a specific scoring model"""
        scoring_model = self.get_object()
        dates_ranges = scoring_model.dates_ranges.all()
        serializer = DatesRangeSerializer(dates_ranges, many=True)
        return Response(serializer.data)


class ValueRangeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing value ranges.
    """
    serializer_class = ValueRangeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ValueRange.objects.filter(scoring_model__owner=self.request.user)

    def perform_create(self, serializer):
        scoring_model_id = self.request.data.get('scoring_model')
        scoring_model = ScoringModel.objects.get(id=scoring_model_id, owner=self.request.user)
        serializer.save(scoring_model=scoring_model)


class DatesRangeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing date ranges.
    """
    serializer_class = DatesRangeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DatesRange.objects.filter(scoring_model__owner=self.request.user)

    def perform_create(self, serializer):
        scoring_model_id = self.request.data.get('scoring_model')
        scoring_model = ScoringModel.objects.get(id=scoring_model_id, owner=self.request.user)
        serializer.save(scoring_model=scoring_model)


class RecommendationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing recommendations.
    """
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recommendation.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        question_id = self.request.data.get('question')
        question = Question.objects.get(id=question_id, owner=self.request.user)
        serializer.save(owner=self.request.user, question=question)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user information.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def token(self, request):
        """Get current user's API token"""
        token = request.user.auth_token
        return Response({'token': token.key})


class AnalyticsViewSet(viewsets.ViewSet):
    """
    API endpoint for analytics and reporting.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def lead_summary(self, request):
        """Get lead analytics summary"""
        user = request.user
        leads = Lead.objects.filter(owner=user)
        
        total_leads = leads.count()
        avg_x_axis = leads.aggregate(avg=Avg('x_axis'))['avg'] or 0
        avg_y_axis = leads.aggregate(avg=Avg('y_axis'))['avg'] or 0
        avg_total_score = leads.aggregate(avg=Avg('total_score'))['avg'] or 0
        
        # Score distribution
        score_ranges = {
            'low': leads.filter(total_score__lt=20).count(),
            'medium': leads.filter(total_score__gte=20, total_score__lt=40).count(),
            'high': leads.filter(total_score__gte=40).count(),
        }
        
        data = {
            'total_leads': total_leads,
            'average_scores': {
                'x_axis': round(avg_x_axis, 2),
                'y_axis': round(avg_y_axis, 2),
                'total': round(avg_total_score, 2),
            },
            'score_distribution': score_ranges,
        }
        
        return Response(data)

    @action(detail=False, methods=['get'])
    def question_analytics(self, request):
        """Get analytics for questions"""
        user = request.user
        questions = Question.objects.filter(owner=user)
        
        question_data = []
        for question in questions:
            # Get answer distribution for this question
            answers = question.answers.all()
            answer_counts = answers.values('response').annotate(count=Count('response'))
            
            question_data.append({
                'id': question.id,
                'number': question.number,
                'text': question.text,
                'type': question.type,
                'field_name': question.field_name,
                'answer_distribution': list(answer_counts),
                'total_answers': answers.count(),
            })
        
        return Response(question_data)

    @action(detail=False, methods=['get'])
    def recommendation_effectiveness(self, request):
        """Get recommendation effectiveness analytics"""
        user = request.user
        recommendations = Recommendation.objects.filter(owner=user)
        
        rec_data = []
        for rec in recommendations:
            # Count how many times this recommendation was triggered
            triggered_count = rec.question.answers.filter(
                lead__owner=user
            ).count()
            
            rec_data.append({
                'id': rec.id,
                'question_text': rec.question.text,
                'rule': rec.rule,
                'response_text': rec.response_text,
                'affiliate_name': rec.affiliate_name,
                'triggered_count': triggered_count,
            })
        
        return Response(rec_data)
