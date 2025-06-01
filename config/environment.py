# config/environment.py

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

class Environment:
    def __init__(self, env_name=None):
        self.env_name = env_name or os.environ.get("ENVIRONMENT", "staging")
        self.config_dir = Path(__file__).parent
        self.env_file = self.config_dir / f".env.{self.env_name}"

        if not self.env_file.exists():
            print(f"❌ Error: Environment file {self.env_file} not found.")
            print(f"Available environments: {self._get_available_environments()}")
            sys.exit(1)

        load_dotenv(dotenv_path=self.env_file, override=True)
        print(f"✅ Loaded environment configuration from {self.env_file}")

    def _get_available_environments(self):
        return [f.name.replace(".env.", "") for f in self.config_dir.glob(".env.*")]
