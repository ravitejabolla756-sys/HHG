import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    serpapi_api_key: str = os.getenv("SERPAPI_API_KEY", "")
    rpc_url: str = os.getenv("POLYGON_AMOY_RPC_URL", "")
    private_key: str = os.getenv("PRIVATE_KEY", "")
    contract_address: str = os.getenv("CONTRACT_ADDRESS", "")
    explorer_base_url: str = os.getenv("EXPLORER_BASE_URL", "https://amoy.polygonscan.com/tx/")
    dry_run: bool = os.getenv("DRY_RUN", "false").lower() == "true"

    def validate(self) -> None:
        required = {"SERPAPI_API_KEY": self.serpapi_api_key, "POLYGON_AMOY_RPC_URL": self.rpc_url, "PRIVATE_KEY": self.private_key, "CONTRACT_ADDRESS": self.contract_address}
        missing = [key for key, value in required.items() if not value]
        if missing and not self.dry_run:
            raise RuntimeError("Missing environment variables: " + ", ".join(missing))
