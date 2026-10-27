"""Document registry: category labels and status per document, loaded from YAML."""
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator

from copilot import config


class SectionOverride(BaseModel):
    status: str
    note: str = ""


class DocEntry(BaseModel):
    categories: list[str]
    rationale: str
    section_overrides: dict[str, SectionOverride] = {}

    @property
    def primary(self) -> str:
        return self.categories[0]


class Registry(BaseModel):
    categories: list[str]
    documents: dict[str, DocEntry]

    @field_validator("documents")
    @classmethod
    def _labels_known(cls, docs, info):
        known = set(info.data.get("categories", []))
        for name, entry in docs.items():
            if not entry.categories:
                raise ValueError(f"{name}: needs at least one category")
            unknown = set(entry.categories) - known
            if unknown:
                raise ValueError(f"{name}: unknown categories {sorted(unknown)}")
        return docs


def load_registry(path: Path = config.REGISTRY_PATH, docs_dir: Path = config.DOCS_DIR) -> Registry:
    registry = Registry.model_validate(yaml.safe_load(path.read_text()))
    on_disk = {p.name for p in docs_dir.glob("*.md")}
    registered = set(registry.documents)
    if on_disk != registered:
        raise ValueError(
            f"registry and docs/ disagree: missing from registry {sorted(on_disk - registered)}, "
            f"missing on disk {sorted(registered - on_disk)}"
        )
    return registry
