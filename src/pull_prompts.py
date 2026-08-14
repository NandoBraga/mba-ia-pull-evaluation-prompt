"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.load import dumpd
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPTS_TO_PULL = [
    {
        "hub_name": "leonanluppi/bug_to_user_story_v1",
        "local_file": "prompts/bug_to_user_story_v1.yml",
        "root_key": "bug_to_user_story_v1"
    },
]

def _extract_prompts(prompt_template) -> dict:
    system_prompt = ""
    user_prompt = ""

    serialized = dumpd(prompt_template)
    messages = serialized["kwargs"]["messages"]

    for message in messages:
        msg_class = message["id"][-1]
        text = message["kwargs"]["prompt"]["kwargs"]["template"]

        if "System" in msg_class:
            system_prompt = text.strip()
        elif "Human" in msg_class:
            user_prompt = text.strip()

    return {"system_prompt": system_prompt, "user_prompt": user_prompt}

def pull_prompts_from_langsmith():

    for cfg in PROMPTS_TO_PULL:
        hub_name = cfg["hub_name"]
        local_file = cfg["local_file"]
        root_key = cfg["root_key"]

        print(f"\n→ Puxando: {hub_name}")

        prompt_template = hub.pull(hub_name)
        extracted = _extract_prompts(prompt_template)

        prompt_data = {
            root_key: {
                "system_prompt": extracted["system_prompt"],
                "user_prompt": extracted["user_prompt"],
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management", "baseline"]
            }
        }

    save_yaml(prompt_data, local_file)
    print(f"Salvo em {local_file}")


def main():
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    try:
        return pull_prompts_from_langsmith()
    except Exception as e:
        print(f"Erro: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
