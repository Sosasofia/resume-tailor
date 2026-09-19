import os


from openai import OpenAI


def create_client() -> OpenAI:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    api_key = os.environ["AZURE_OPENAI_API_KEY"]

    return OpenAI(
        base_url=endpoint,
        api_key=api_key,
    )


def get_deployment() -> str:
    return os.environ["AZURE_OPENAI_DEPLOYMENT"]