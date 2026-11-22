from marshmallow import fields

from superset.db_engine_specs.base import (
    BaseEngineSpec,
    BasicParametersType,
    DatabaseCategory,
)
from superset.db_engine_specs.postgres import (
    PostgresEngineSpec,
    PostgresParametersSchema,
)


class MaterializeParametersSchema(PostgresParametersSchema):
    """Postgres connection parameters plus the Materialize cluster."""

    materializedb_cluster = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "Materialize cluster to run queries on"},
    )


class MaterializeEngineSpec(PostgresEngineSpec):
    engine = "materialize"
    engine_name = "Materialize"
    
    default_driver = "psycopg2"
    parameters_schema = MaterializeParametersSchema()

    @classmethod
    def build_sqlalchemy_uri(
        cls,
        parameters: BasicParametersType,
        encrypted_extra: dict[str, str] | None = None,
    ) -> str:
        """Pass the form's cluster to Materialize as ``options=--cluster=<name>``."""
        if cluster := parameters.get("materializedb_cluster"):
            query = {**parameters.get("query", {}), "options": f"--cluster={cluster}"}
            parameters = {**parameters, "query": query}
        return super().build_sqlalchemy_uri(parameters, encrypted_extra)
    
    # TODO: Fix the URI after making the dialect, also for connection_string
    sqlalchemy_uri_placeholder = (
        "materialize+psycopg2://username:password@host:port/database"
    )
    
    metadata = {
        # Required fields
        "description": "A brief description of the database.",
        "categories": [
            DatabaseCategory.CLOUD_AWS,
            DatabaseCategory.TRADITIONAL_RDBMS,
            DatabaseCategory.OPEN_SOURCE,
        ],
        # TODO: Add package name for SQLAlchemy dialect after making it
        "pypi_packages": ["psycopg2", "sqlalchemy-materialize"],
        "connection_string": 
            "materialize+psycopg2://{username}:{password}@{host}:{port}/{database}",

        # Recommended fields
        "logo": "materialize.svg",  # TODO: Logo file in docs/static/img/databases/
        "homepage_url": "https://materialize.com/",
        "default_port": 6875,
    }
    
    
    # NOTES: 
    # - Time grains inherited from Postgres work. Tested in Materialize Console.
    # - TODO: Test in SQLLab once pg_catalog.pg_opclass thingy is fixed
    # I think I fixed pg_opclass in the dialect, but there's more to fix
    # e.g. afaik, foreign key is not supported in Materialize.
    # and theres like get_foreign_key() function or similar in the dialect.