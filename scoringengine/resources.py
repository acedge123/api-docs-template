from attr import fields
from import_export import fields, resources

from scoringengine.models import Lead


class LeadResource(resources.ModelResource):
    customer_email = fields.Field(attribute="customer_email")
    customer_id = fields.Field(attribute="customer_id")

    class Meta:
        model = Lead
        fields = (
            "lead_id",
            "timestamp",
            "x_axis",
            "y_axis",
            "total_score",
            "customer_email",
            "customer_id",
        )
