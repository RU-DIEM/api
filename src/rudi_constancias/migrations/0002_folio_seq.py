from django.db import migrations

########################################################################################


class Migration(migrations.Migration):
    dependencies = [("rudiconstancias", "0001_initial")]

    # read by `trg_constancia_folio_asignar`; a number burned by a rolled back
    # transaction leaves a harmless gap, never a repeated folio
    operations = [
        migrations.RunSQL(
            reverse_sql="DROP SEQUENCE IF EXISTS rudiconstancias_folio_seq;",
            sql="CREATE SEQUENCE IF NOT EXISTS rudiconstancias_folio_seq;",
        ),
    ]
