from rest_framework import serializers

from scoringengine.models import Lead, Answer


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
        lead = Lead.objects.create(**validated_data)

        for answer_data in answers_data:
            Answer.objects.create(lead=lead, **answer_data)

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
