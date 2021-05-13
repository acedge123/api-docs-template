from rest_framework import serializers

from scoringengine.models import Question, Choice, Lead, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['text']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['number', 'field_name', 'text', 'choices']


class AnswerSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['field_name', 'response']


class LeadSerializerCreate(serializers.ModelSerializer):
    answers = AnswerSerializerCreate(many=True, required=True)

    class Meta:
        model = Lead
        fields = ['lead_id', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        lead = Lead.objects.create(**validated_data)

        for answer_data in answers_data:
            Answer.objects.create(lead=lead, **answer_data)

        return lead


class AnswerSerializerView(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['response_text', 'affiliate_name', 'affiliate_image', 'affiliate_link']


class LeadSerializerView(serializers.HyperlinkedModelSerializer):
    recommendations = AnswerSerializerView(many=True, source='answers')

    class Meta:
        model = Lead
        fields = ['url', 'lead_id', 'x_axis', 'y_axis', 'recommendations']
        extra_kwargs = {
            'url': {'view_name': 'api:v1:lead-detail'}
        }

    def to_representation(self, instance):
        result = super().to_representation(instance)

        # Clean-up empty recommendations
        non_empty_recommendations = [r for r in result['recommendations'] if r['response_text']]
        result['recommendations'] = non_empty_recommendations

        return result
