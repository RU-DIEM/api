# applies to every suite under `src`, so the template tests that rudi replaces
# stay deselected however the run is scoped
from rudi_tests.deselect import pytest_collection_modifyitems

__all__ = ("pytest_collection_modifyitems",)
