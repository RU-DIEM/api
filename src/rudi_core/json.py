from django.db.models import CharField, Transform

########################################################################################


class JsonTypeof(Transform):
    function = "jsonb_typeof"
    lookup_name = "typeof"
    output_field = CharField()
