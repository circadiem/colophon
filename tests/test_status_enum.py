"""CLAUDE.md §3: exactly eight status values, display forms with the interpunct, no ninth value."""

from colophon.channels import Reason, Status

EXPECTED = {
    "EXCLUDED_WFH": "EXCLUDED·WFH",
    "PUBLIC_DOMAIN": "PUBLIC·DOMAIN",
    "NEVER_GRANTED": "NEVER·GRANTED",
    "REVERTED_LIKELY": "REVERTED·LIKELY",
    "TERMINABLE_NOW": "TERMINABLE·NOW",
    "TERMINABLE_FUTURE": "TERMINABLE·FUTURE",
    "LAPSED_WINDOW": "LAPSED·WINDOW",
    "GRANTED_ACTIVE": "GRANTED·ACTIVE",
}


def test_exactly_eight_values_in_order():
    assert [s.name for s in Status] == list(EXPECTED)


def test_display_forms_use_interpunct():
    for status in Status:
        assert status.display == EXPECTED[status.name]
        assert status.display == status.name.replace("_", "·")


def test_undetermined_reasons_are_not_statuses():
    """Undetermined is a distinct result, never a status value (Step 0 answer 2.4)."""
    assert not set(r.name for r in Reason) & set(s.name for s in Status)
    for required in (
        "EXECUTION_DATE_REQUIRED",
        "CONVEYANCE_UNKNOWN",
        "GRANTOR_OUT_OF_SCOPE",
        "STRADDLES_AS_OF",
        "GRANT_PREDATES_SECURED_COPYRIGHT",
    ):
        assert required in Reason.__members__
