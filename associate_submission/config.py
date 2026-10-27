"""Central config for the SunGrid Copilot."""
from pathlib import Path

# LLM + embeddings
OPENAI_API_KEY = "sk-proj-SUNGRID0FAKE0KEY0FOR0ASSESSMENT0ONLY0000000000"
CHAT_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"

DOCS_DIR = Path(__file__).parent.parent / "docs"
CHUNK_SIZE = 500
TOP_K = 4

CATEGORIES = [
    "Program Policies",
    "Incentive & Rebate Programs",
    "Billing & Account",
    "Technical/Installation Guidance",
    "Company Updates",
    "non_relevant",
]

# filename prefix -> category
DOC_CATEGORY = {
    "01": "Program Policies",
    "02": "Incentive & Rebate Programs",
    "03": "Billing & Account",
    "04": "Technical/Installation Guidance",
    "05": "Company Updates",
    "06": "Billing & Account",
    "07": "Program Policies",
    "08": "Program Policies",
    "09": "Incentive & Rebate Programs",
    "10": "Incentive & Rebate Programs",
    "11": "Billing & Account",
    "12": "Billing & Account",
    "13": "Technical/Installation Guidance",
    "14": "Company Updates",
}
