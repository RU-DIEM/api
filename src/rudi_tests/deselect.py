from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

    import pytest

########################################################################################

# template tests for endpoints rudi took over with a different contract. Each one
# has a rudi counterpart covering the same behavior, named in its reason.
# Deselecting them, instead of editing the template's test files, keeps factory
# merges free of conflicts in `api_tests`.

REPLACED_TEMPLATE_TESTS: Final[Mapping[str, str]] = dict.fromkeys(
    (
        "test_api/test_accounts.py::test_register_is_public",
        "test_api/test_accounts.py::test_register_hashes_the_password",
        "test_api/test_accounts.py::test_register_never_echoes_the_password",
        "test_api/test_accounts.py::test_register_rejects_mismatched_passwords",
        "test_api/test_accounts.py::test_register_rejects_weak_passwords",
        "test_api/test_accounts.py::test_register_rejects_duplicate_usernames",
        "test_api/test_accounts.py::test_register_rejects_invalid_email",
        "test_api/test_accounts.py::test_register_rejects_a_non_client_group",
        "test_api/test_accounts.py::test_register_normalizes_the_username",
        "test_api/test_email.py::test_registration_waits_for_the_confirmed_address",
    ),
    "/auth/register/ is rudi's registration; see rudi_tests/test_api/test_register.py",
)

########################################################################################


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    replaced: list[pytest.Item] = [
        item
        for item in items
        if item.nodeid.removeprefix("src/api_tests/") in REPLACED_TEMPLATE_TESTS
    ]

    if not replaced:
        return

    config.hook.pytest_deselected(items=replaced)

    items[:] = [item for item in items if item not in replaced]
