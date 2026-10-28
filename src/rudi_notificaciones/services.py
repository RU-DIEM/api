from typing import TYPE_CHECKING, Final

from django.core.mail import send_mail
from django.db.models import F
from django.db.transaction import on_commit
from django.utils.timezone import now

from rudi_notificaciones.models import Notificacion

if TYPE_CHECKING:
    from uuid import UUID

    from rudi_catalogos.models import PlantillaMensaje

########################################################################################

MAX_INTENTOS: Final[int] = 5

########################################################################################


def encolar(
    *,
    asunto: str,
    cuenta_id: UUID | None = None,
    cuerpo: str,
    destinatario: str,
    plantilla: PlantillaMensaje,
) -> Notificacion:
    """
    Queue a rendered message inside the caller's transaction.

    The send itself waits for the commit: a rolled back write never mails
    anyone, and a mail provider failure never rolls back the write; the
    queue keeps the message for `enviar_pendientes` to retry.

    Returns:
        The queued notification.

    """

    notificacion: Notificacion = Notificacion.objects.create(
        asunto=asunto,
        cuenta_id=cuenta_id,
        cuerpo=cuerpo,
        destinatario=destinatario,
        plantilla=plantilla,
    )

    on_commit(lambda: enviar(notificacion.pk))

    return notificacion


def enviar(notificacion_id: UUID) -> bool:
    """
    Try to deliver one queued message; record the outcome either way.

    Returns:
        Whether it was delivered.

    """

    notificacion: Notificacion | None = Notificacion.objects.filter(
        descartada_at__isnull=True,
        enviada_at__isnull=True,
        pk=notificacion_id,
    ).first()

    if notificacion is None:
        return False

    fila = Notificacion.objects.filter(pk=notificacion_id)

    try:
        send_mail(
            fail_silently=False,
            from_email=None,
            message=notificacion.cuerpo,
            recipient_list=[notificacion.destinatario],
            subject=notificacion.asunto,
        )
    except Exception as e:  # ruff: ignore[blind-except]
        # whatever the provider raised, the message stays queued for a retry,
        # until it has failed often enough to stop trying
        intentos: int = notificacion.intentos + 1  # ty: ignore[unsupported-operator]

        fila.update(
            descartada_at=(now() if intentos >= MAX_INTENTOS else None),
            intentos=F("intentos") + 1,
            ultimo_error=(str(e) or e.__class__.__name__)[:2_000],
        )

        return False

    fila.update(enviada_at=now(), intentos=F("intentos") + 1)

    return True


def enviar_pendientes() -> int:
    """
    Deliver what is due and retry what failed (procesos.md).

    Returns:
        How many messages were delivered.

    """

    return sum(
        enviar(pk)
        for pk in Notificacion.objects
        .filter(
            descartada_at__isnull=True,
            enviada_at__isnull=True,
            programada_para__lte=now(),
        )
        .order_by("programada_para")
        .values_list("pk", flat=True)
    )
