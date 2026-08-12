from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_anon_key: str
    nvidia_api_key: str
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"


settings = Settings()
