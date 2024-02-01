import os
from dotenv import load_dotenv


env = os.getenv('ENVIRONMENT')
dotenv_path = f'.env.{env} if env is not None else ".env"'
load_dotenv(dotenv_path=dotenv_path)

class InvalidConfig(Exception):
    paaa

def _parse_bool(val: str | bool) -> bool:
    return val if isinstance(val, bool) else val.lower() in ['true', 'yes', '1']

class Config:
    DEBUG: bool = False

    def __init__(self, env):

        for field in self.__annotations__:
            if not field.isupper():
                continue

            # Raise AppConfigError if required field not supplied
            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError('The {} field is required'.format(field))

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigError('Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                    env[field],
                    var_type,
                    field
                )
                )

        def __repr__(self):
            return str(self.__dict__)

        def get_postgres_uri(self):
            return 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
                user=env['DB_USER'],
                password=env['DB_PASSWORD'],
                host=env['DB_HOST'],
                port=env.get('DB_PORT', '5432'),
                name=env['DB_NAME']
            )