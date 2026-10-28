# ruff: file-ignore[non-empty-init-module]

from typing import TYPE_CHECKING

from pgtrigger import (
    After,
    AnyChange,
    Before,
    Deferred,
    Insert,
    Trigger,
    Update,
    register as register_trigger,
)

from api_auth.models import ApiUser
from api_utils.strings import normalize_trigger
from rudi_auth.models import RudiUser
from rudi_estados.models import EstadoRudiUser

from .academia import Carrera, Facultad, Institucion
from .docente import DocenteProfile
from .estudiante import EstudianteCarrera, EstudianteProfile
from .externo import ExternoProfile
from .mentor import MentorAreaExperiencia, MentorCertificacion, MentorProfile

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Final

########################################################################################

__all__: Sequence[str] = (
    "Carrera",
    "DocenteProfile",
    "EstudianteCarrera",
    "EstudianteProfile",
    "ExternoProfile",
    "Facultad",
    "Institucion",
    "MentorAreaExperiencia",
    "MentorCertificacion",
    "MentorProfile",
)

########################################################################################

PERFILES: Final[str] = " UNION ALL ".join(
    f"SELECT 1 FROM {model._meta.db_table} WHERE user_id = NEW.id"  # ruff: ignore[hardcoded-sql-expression, private-member-access]
    for model in (DocenteProfile, EstudianteProfile, ExternoProfile, MentorProfile)
)

MIN_PROFILE_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    require boolean;
BEGIN
    SELECT allow_inscripcion
    INTO require
    FROM {EstadoRudiUser._meta.db_table}
    WHERE id = NEW.estado_id;
    IF require AND NOT EXISTS ({PERFILES}) THEN
        RAISE check_violation
        USING
            COLUMN = 'estado_id',
            MESSAGE = 'Una cuenta no puede activarse sin ningún perfil declarado.';
    END IF;
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

MIN_CARRERA_TRIGGER: Final[str] = normalize_trigger(f"""
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM {EstudianteCarrera._meta.db_table}
        WHERE profile_id = NEW.id
    ) THEN
        RAISE check_violation
        USING
            COLUMN = 'id',
            MESSAGE = 'Un perfil de estudiante exige al menos una carrera declarada.';
    END IF;
    RETURN NULL;
END;
""")  # ruff: ignore[hardcoded-sql-expression, private-member-access]

EMAIL_DOMINIO_TRIGGER: Final[str] = normalize_trigger(f"""
DECLARE
    dominio text;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM {EstudianteProfile._meta.db_table}
        AS profile
        JOIN {RudiUser._meta.db_table}
        AS persona
        ON persona.id = profile.user_id
        WHERE persona.user_id = NEW.id
    ) THEN
        RETURN NEW;
    END IF;
    dominio := rudi_parametro('registro.dominio_institucional') #>> '{{}}';
    IF dominio IS NULL OR dominio = '' THEN
        RETURN NEW;
    END IF;
    IF lower(NEW.email) NOT LIKE '%@' || lower(dominio) THEN
        RAISE check_violation
        USING
            COLUMN = 'email',
            MESSAGE = 'Una cuenta con perfil de estudiante UAM exige un correo del dominio institucional.';
    END IF;
    RETURN NEW;
END;
""")  # ruff: ignore[hardcoded-sql-expression, line-too-long, private-member-access]

########################################################################################

register_trigger(
    Trigger(
        condition=AnyChange("email"),
        name="trg_apiuser_email_domain_check",
        operation=Update,
        when=Before,
        func=EMAIL_DOMINIO_TRIGGER,
    ),
)(ApiUser)

register_trigger(
    Trigger(
        name="trg_estudianteprofile_carrera",
        operation=Insert,
        timing=Deferred,
        when=After,
        func=MIN_CARRERA_TRIGGER,
    ),
)(EstudianteProfile)

register_trigger(
    Trigger(
        name="trg_rudiuser_profile",
        operation=Update,
        timing=Deferred,
        when=After,
        func=MIN_PROFILE_TRIGGER,
    ),
)(RudiUser)
