from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Staff Portal"
    environment: str = "dev"
    api_prefix: str = "/api"

    database_url: str = "postgresql+psycopg2://postgres:Astra_DB_S3cr3t_99!@postgres:5432/bhack"

    session_cookie_name: str = "token"
    session_ttl_hours: int = 24
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    cors_origins: str = "http://localhost:5173,http://localhost:3001"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
