from django.utils.timezone import now
from rest_framework import serializers

from scoringengine.models import (
    Lead, Answer, Question, Choice, ScoringModel,
    ValueRange, DatesRange, Recommendation
)
from users.models import User


class AnswerSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["field_name", "response"]


class LeadSerializerCreate(serializers.ModelSerializer):
    answers = AnswerSerializerCreate(many=True, required=True)

    class Meta:
        model = Lead
        fields = ["lead_id", "answers"]

    def to_internal_value(self, data):
        # Reformat answers dict to list
        data["answers"] = [
            {"field_name": fn, "response": r} for fn, r in data["answers"].items()
        ]

        return super().to_internal_value(data)

    def create(self, validated_data):
        answers_data = validated_data.pop("answers")
        validated_data["timestamp"] = now()
        lead = Lead.objects.create(**validated_data)

        for answer_data in answers_data:
            # Handle values field specially for SQLite compatibility
            values = answer_data.pop('values', None)
            answer = Answer.objects.create(lead=lead, **answer_data)
            if values is not None:
                answer.set_values(values)
                answer.save()

        return lead


class AnswerSerializerView(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            "field_name",
            "response_text",
            "affiliate_name",
            "affiliate_image",
            "affiliate_link",
            "redirect_url",
        ]


class LeadSerializerView(serializers.ModelSerializer):
    recommendations = AnswerSerializerView(many=True, source="answers")

    class Meta:
        model = Lead
        fields = ["lead_id", "x_axis", "y_axis", "total_score", "recommendations"]

    def to_representation(self, instance):
        result = super().to_representation(instance)

        fields_to_check = [
            "response_text",
            "affiliate_name",
            "affiliate_image",
            "affiliate_link",
            "redirect_url",
        ]

        # Clean-up empty recommendations, reformat recommendations list to dict
        non_empty_recommendations = {
            r.pop("field_name"): r
            for r in result["recommendations"]
            if any([r[f] for f in fields_to_check])
        }
        result["recommendations"] = non_empty_recommendations

        return result


# Admin Serializers
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'slug', 'value']


class ValueRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValueRange
        fields = ['id', 'start', 'end', 'points']


class DatesRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatesRange
        fields = ['id', 'start', 'end', 'points']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = [
            'id', 'rule', 'response_text', 'affiliate_name',
            'affiliate_image', 'affiliate_link', 'redirect_url'
        ]


class ScoringModelSerializer(serializers.ModelSerializer):
    value_ranges = ValueRangeSerializer(many=True, read_only=True)
    dates_ranges = DatesRangeSerializer(many=True, read_only=True)

    class Meta:
        model = ScoringModel
        fields = [
            'id', 'weight', 'x_axis', 'y_axis', 'formula',
            'value_ranges', 'dates_ranges'
        ]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    scoring_model = ScoringModelSerializer(read_only=True)
    recommendation = RecommendationSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'number', 'text', 'field_name', 'multiple_values',
            'type', 'min_value', 'max_value', 'choices', 'scoring_model', 'recommendation'
        ]

    def validate_field_name(self, value):
        """Validate field name format"""
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
            raise serializers.ValidationError(
                "Field name must start with a letter or underscore and contain only letters, numbers, and underscores."
            )
        return value

    def validate(self, data):
        """Validate question data"""
        # Check if field_name is unique for this user
        user = self.context['request'].user
        field_name = data.get('field_name')
        question_id = self.instance.id if self.instance else None

        existing_question = Question.objects.filter(
            owner=user,
            field_name=field_name
        ).exclude(id=question_id).first()

        if existing_question:
            raise serializers.ValidationError({
                'field_name': f'A question with field name "{field_name}" already exists.'
            })

        # Validate min_value and max_value for slider type
        if data.get('type') == Question.SLIDER:
            min_value = data.get('min_value')
            max_value = data.get('max_value')
            if min_value is not None and max_value is not None and min_value >= max_value:
                raise serializers.ValidationError({
                    'min_value': 'Min value must be less than max value for slider questions.'
                })

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['id', 'is_staff']


class LeadAnalyticsSerializer(serializers.Serializer):
    total_leads = serializers.IntegerField()
    average_scores = serializers.DictField()
    score_distribution = serializers.DictField()
