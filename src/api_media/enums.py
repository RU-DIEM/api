from django.db.models import TextChoices

########################################################################################


class MediaVisibility(TextChoices):
    PRIVATE = "private"
    PUBLIC = "public"
