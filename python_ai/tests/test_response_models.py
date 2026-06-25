import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from response_models import MetadataResult, TagResult, KeywordResult, StyleResult, DescriptionResult

def test_metadata_result_to_dict():
    metadata = MetadataResult(
        tags=["a"],
        keywords=["b"],
        style=StyleResult(style="Copperplate", confidence=90, reason="Test"),
        description=DescriptionResult(description="A test description.")
    )
    
    result = metadata.to_dict()
    
    assert result == {
        "tags": ["a"],
        "keywords": ["b"],
        "style": {
            "style": "Copperplate",
            "confidence": 90,
            "reason": "Test"
        },
        "description": {
            "description": "A test description."
        }
    }
