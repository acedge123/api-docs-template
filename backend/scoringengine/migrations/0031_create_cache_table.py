# Generated manually for cache table creation

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("scoringengine", "0030_add_database_optimizations"),
    ]

    operations = [
        # Create cache table for database caching
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS cache_table (
                cache_key varchar(255) NOT NULL PRIMARY KEY,
                value text NOT NULL,
                expires timestamp with time zone NOT NULL
            );
            CREATE INDEX IF NOT EXISTS cache_table_expires_idx ON cache_table (expires);
            """,
            reverse_sql="DROP TABLE IF EXISTS cache_table;",
        ),
    ]
