# Generated manually for database optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scoringengine', '0029_answerlog_leadlog'),
    ]

    operations = [
        # Add indexes for frequently queried fields
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['owner'], name='question_owner_idx'),
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['field_name'], name='question_field_name_idx'),
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['owner', 'number'], name='question_owner_number_idx'),
        ),
        
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['owner'], name='lead_owner_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['timestamp'], name='lead_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(fields=['owner', 'timestamp'], name='lead_owner_timestamp_idx'),
        ),
        
        migrations.AddIndex(
            model_name='leadlog',
            index=models.Index(fields=['owner'], name='leadlog_owner_idx'),
        ),
        migrations.AddIndex(
            model_name='leadlog',
            index=models.Index(fields=['timestamp'], name='leadlog_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='leadlog',
            index=models.Index(fields=['owner', 'timestamp'], name='leadlog_owner_timestamp_idx'),
        ),
        
        migrations.AddIndex(
            model_name='answer',
            index=models.Index(fields=['lead'], name='answer_lead_idx'),
        ),
        migrations.AddIndex(
            model_name='answer',
            index=models.Index(fields=['field_name'], name='answer_field_name_idx'),
        ),
        migrations.AddIndex(
            model_name='answer',
            index=models.Index(fields=['lead', 'field_name'], name='answer_lead_field_name_idx'),
        ),
        
        migrations.AddIndex(
            model_name='answerlog',
            index=models.Index(fields=['lead'], name='answerlog_lead_idx'),
        ),
        migrations.AddIndex(
            model_name='answerlog',
            index=models.Index(fields=['field_name'], name='answerlog_field_name_idx'),
        ),
        
        migrations.AddIndex(
            model_name='choice',
            index=models.Index(fields=['question'], name='choice_question_idx'),
        ),
        migrations.AddIndex(
            model_name='choice',
            index=models.Index(fields=['question', 'slug'], name='choice_question_slug_idx'),
        ),
        
        migrations.AddIndex(
            model_name='scoringmodel',
            index=models.Index(fields=['owner'], name='scoringmodel_owner_idx'),
        ),
        migrations.AddIndex(
            model_name='scoringmodel',
            index=models.Index(fields=['question'], name='scoringmodel_question_idx'),
        ),
        
        migrations.AddIndex(
            model_name='valuerange',
            index=models.Index(fields=['scoring_model'], name='valuerange_scoring_model_idx'),
        ),
        migrations.AddIndex(
            model_name='valuerange',
            index=models.Index(fields=['scoring_model', 'start'], name='valuerange_scoring_model_start_idx'),
        ),
        migrations.AddIndex(
            model_name='valuerange',
            index=models.Index(fields=['scoring_model', 'end'], name='valuerange_scoring_model_end_idx'),
        ),
        
        migrations.AddIndex(
            model_name='datesrange',
            index=models.Index(fields=['scoring_model'], name='datesrange_scoring_model_idx'),
        ),
        migrations.AddIndex(
            model_name='datesrange',
            index=models.Index(fields=['scoring_model', 'start'], name='datesrange_scoring_model_start_idx'),
        ),
        migrations.AddIndex(
            model_name='datesrange',
            index=models.Index(fields=['scoring_model', 'end'], name='datesrange_scoring_model_end_idx'),
        ),
        
        migrations.AddIndex(
            model_name='recommendation',
            index=models.Index(fields=['owner'], name='recommendation_owner_idx'),
        ),
        migrations.AddIndex(
            model_name='recommendation',
            index=models.Index(fields=['question'], name='recommendation_question_idx'),
        ),
        
        # Add check constraints for data validation
        migrations.AddConstraint(
            model_name='question',
            constraint=models.CheckConstraint(
                check=models.Q(number__gte=1),
                name='question_number_positive'
            ),
        ),
        
        migrations.AddConstraint(
            model_name='scoringmodel',
            constraint=models.CheckConstraint(
                check=models.Q(weight__gte=0),
                name='scoringmodel_weight_positive'
            ),
        ),
        
        migrations.AddConstraint(
            model_name='valuerange',
            constraint=models.CheckConstraint(
                check=models.Q(points__gte=0),
                name='valuerange_points_positive'
            ),
        ),
        
        migrations.AddConstraint(
            model_name='datesrange',
            constraint=models.CheckConstraint(
                check=models.Q(points__gte=0),
                name='datesrange_points_positive'
            ),
        ),
        
        # Add partial indexes for better performance
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(
                fields=['total_score'],
                name='lead_high_score_idx',
                condition=models.Q(total_score__gte=40)
            ),
        ),
        
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(
                fields=['x_axis', 'y_axis'],
                name='lead_xy_axes_idx'
            ),
        ),
    ]
