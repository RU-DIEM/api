# ruff: ignore[implicit-namespace-package]

"""
Railway IaC configuration for deployment.
"""

from typing import Final

import railway_sdk as rsdk

########################################################################################

RESOURCE_LIMITS: Final[dict[str, dict]] = {
    "containers": {"cpu": 2, "memoryBytes": 2_000_000_000}
}

REGION: Final[str] = "us-east4-eqdc4a"
VOLUME_ALERTS: Final[dict[str, dict]] = {"usage": {"100": {}, "95": {}, "80": {}}}
VOLUME_SIZE: Final[int] = 50_000

########################################################################################

DEPLOY_CONFIG: Final[dict] = {
    "limitOverride": RESOURCE_LIMITS,
    "restartPolicyMaxRetries": 3,
}

########################################################################################

DB_DEPLOY_CONFIG: Final[dict] = DEPLOY_CONFIG | {
    "drainingSeconds": 20,
    "multiRegionConfig": {REGION: {"numReplicas": 1}},
    "overlapSeconds": 0,
}

SERVICE_DEPLOY_CONFIG: Final[dict] = DEPLOY_CONFIG | {
    "drainingSeconds": 10,
    "overlapSeconds": 20,
}

########################################################################################

VOLUME_CONFIG: Final[dict] = {
    "alerts": VOLUME_ALERTS,
    "allowOnlineResize": True,
    "region": REGION,
    "sizeMB": VOLUME_SIZE,
}

########################################################################################


@rsdk.define_railway
def main(ctx: rsdk.RailwayContext | None = None) -> rsdk.Project:  # ruff: ignore[unused-function-argument]
    api = rsdk.service(
        build={
            "buildEnvironment": "V3",
            "builder": "DOCKERFILE",
            "dockerfilePath": "dockerfile",
            "watchPatterns": [
                ".railway/**",
                "dockerfile",
                "pyproject.toml",
                "uv.lock",
                "src/**/*.py",
            ],
        },
        deploy=SERVICE_DEPLOY_CONFIG,
        env={
            "BUNNY_PRIVATE_PULL_ZONE_HOST": rsdk.preserve(),
            "BUNNY_PULL_ZONE_HOST": rsdk.preserve(),
            "BUNNY_SIGNED_URL_TTL_SECONDS": rsdk.preserve(),
            "BUNNY_STORAGE_API_KEY": rsdk.preserve(),
            "BUNNY_STORAGE_HOST": rsdk.preserve(),
            "BUNNY_STORAGE_ZONE": rsdk.preserve(),
            "BUNNY_TOKEN_AUTH_KEY": rsdk.preserve(),
            "DATABASE_URL": rsdk.preserve(),
            "DEBUG": rsdk.preserve(),
            "DEFAULT_FROM_EMAIL": rsdk.preserve(),
            "DEPLOY": rsdk.preserve(),
            "DJANGO_SUPERUSER_PASSWORD": rsdk.preserve(),
            "DJANGO_SUPERUSER_USERNAME": rsdk.preserve(),
            "EMAIL_BACKEND": rsdk.preserve(),
            "EMAIL_HOST": rsdk.preserve(),
            "EMAIL_HOST_PASSWORD": rsdk.preserve(),
            "EMAIL_HOST_USER": rsdk.preserve(),
            "EMAIL_PORT": rsdk.preserve(),
            "EMAIL_USE_TLS": rsdk.preserve(),
            "FRONTEND_URL": rsdk.preserve(),
            "GRANIAN_HOST": rsdk.preserve(),
            "GRANIAN_INTERFACE": rsdk.preserve(),
            "GRANIAN_LOG_ACCESS_ENABLED": rsdk.preserve(),
            "GRANIAN_PORT": rsdk.preserve(),
            "GRANIAN_RELOAD_PATHS": rsdk.preserve(),
            "GRANIAN_WORKERS": rsdk.preserve(),
            "GRANIAN_WORKING_DIR": rsdk.preserve(),
            "GRANIAN_WS": rsdk.preserve(),
            "JWT_SECRET_KEY": rsdk.preserve(),
            "MEDIA_ALLOWED_TYPES": rsdk.preserve(),
            "REDIS_SECRET_KEY": rsdk.preserve(),
            "REDIS_URL": rsdk.preserve(),
            "REQUIRE_EMAIL_VERIFICATION": rsdk.preserve(),
            "SECRET_KEY": rsdk.preserve(),
            "SKIP_SEEDERS": rsdk.preserve(),
            "TOTP_ISSUER": rsdk.preserve(),
        },
        healthcheck="/health/",
        healthcheckTimeout=60,
        name="api",
        preDeploy="python src/manage.py migrate",
        replicas={REGION: 1},
        source=rsdk.github(
            branch="main",
            checkSuites=True,
            repo="jp-zuniga/backend-factory",
        ),
        start="granian api_core.asgi:application --access-log",
    )

    postgres_db = rsdk.postgres("postgres").with_fields(deploy=DB_DEPLOY_CONFIG)
    postgres_volume = rsdk.volume("postgres-volume", **VOLUME_CONFIG)

    redis_db = rsdk.redis("redis").with_fields(
        deploy={
            **DB_DEPLOY_CONFIG,
            "startCommand": '/bin/sh -c "rm -rf $RAILWAY_VOLUME_MOUNT_PATH/lost+found/ && exec docker-entrypoint.sh redis-server --requirepass $REDIS_PASSWORD --save 60 1 --dir $RAILWAY_VOLUME_MOUNT_PATH"',  # ruff: ignore[line-too-long]
        },
    )

    redis_volume = rsdk.volume("redis-volume", **VOLUME_CONFIG)

    return rsdk.project(
        name="api",
        resources=[
            api,
            postgres_db,
            postgres_volume,
            redis_db,
            redis_volume,
        ],
    )
