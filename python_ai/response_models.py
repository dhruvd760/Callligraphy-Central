import dataclasses
from typing import List, Dict, Any

@dataclasses.dataclass
class TagResult:
    tags: List[str]

@dataclasses.dataclass
class KeywordResult:
    keywords: List[str]

@dataclasses.dataclass
class StyleResult:
    style: str
    confidence: int
    reason: str

@dataclasses.dataclass
class LanguageResult:
    language: str

@dataclasses.dataclass
class DescriptionResult:
    description: str

@dataclasses.dataclass
class TitleResult:
    title: str

@dataclasses.dataclass
class MetadataResult:
    tags: List[str]
    keywords: List[str]
    style: StyleResult
    description: DescriptionResult

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tags": self.tags,
            "keywords": self.keywords,
            "style": dataclasses.asdict(self.style),
            "description": dataclasses.asdict(self.description)
        }
