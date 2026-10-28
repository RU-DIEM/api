from typing import TYPE_CHECKING

from django.db import migrations

if TYPE_CHECKING:
    from typing import Final

########################################################################################

# `rudi_parametro` answers `NULL` for a missing or deactivated parameter,
# so every trigger decides for itself what an unset parameter means
FORWARD: Final[str] = """
CREATE OR REPLACE FUNCTION public.rudi_parametro(codigo_param text)
RETURNS jsonb
LANGUAGE sql
STABLE
PARALLEL SAFE
AS $$
    SELECT valor
    FROM rudicatalogos_parametro
    WHERE codigo = codigo_param
    AND is_active
$$;

CREATE OR REPLACE FUNCTION public.rudi_actor()
RETURNS text
LANGUAGE sql
STABLE
PARALLEL SAFE
AS $$ SELECT nullif(current_setting('rudi.actor', true), '') $$;

CREATE OR REPLACE FUNCTION public.rudi_hoy()
RETURNS date
LANGUAGE sql
STABLE
PARALLEL SAFE
AS $$ SELECT (now() AT TIME ZONE 'America/Managua')::date $$;
"""

REVERSE: Final[str] = """
DROP FUNCTION IF EXISTS public.rudi_parametro(text);
DROP FUNCTION IF EXISTS public.rudi_actor();
DROP FUNCTION IF EXISTS public.rudi_hoy();
"""

########################################################################################


class Migration(migrations.Migration):
    initial = True

    dependencies = [("rudicatalogos", "0001_initial")]

    operations = [migrations.RunSQL(reverse_sql=REVERSE, sql=FORWARD)]
