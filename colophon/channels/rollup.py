"""The rollup rule: from per-grant, per-channel results to a reported position.

Governing text: "The triple, and the rollup rule" (Step 2 answers), pending doc edits to docs/II
§01 and CLAUDE.md §3.

    The grant is the unit of computation. Status is computed per grant, per channel.
    The triple (work, right_type, territory) is the unit of reporting. It carries a rolled-up
    position plus its constituent per-grant statuses, never a single status that hides them.

Three levels:

    Level 1 — across channels, within one grant.        Disjunctive: best available route wins.
    Level 2 — across grants, within one contribution.   Disjunctive: any live route makes the
                                                        contribution available by that route.
    Level 3 — across contributions.                     Conjunctive: the triple's position is the
                                                        weakest contribution's position.

Precedence, most actionable first:

    NEVER_GRANTED > REVERTED_LIKELY > TERMINABLE_NOW > TERMINABLE_FUTURE > GRANTED_ACTIVE > LAPSED_WINDOW

EXCLUDED_WFH and PUBLIC_DOMAIN are not on the ladder. They are terminal: nothing for any channel
to return. PUBLIC_DOMAIN short-circuits at the work level before this runs and is not computed
here.

Undetermined results (no status) are not on the ladder either. Two readings the answers do not
state, applied here and flagged in docs/backlog.md:
- Disjunctive levels ignore an Undetermined when any sibling has a status; a level whose
  constituents are all Undetermined has no position.
- The conjunctive level treats a contribution with no position as unknown, which makes the
  triple unknown, unless another contribution is terminal, in which case the triple is blocked:
  a known blocker dominates an unknown.
- A grant whose contribution is unrecorded forms its own contribution group; it is not assumed
  to cover both.

`contribution` stays an attribute of the grant, not a fourth axis of the triple.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Contribution, Grant, RightType
from .results import ChannelResult, StatusResult
from .status import Status

LADDER: tuple[Status, ...] = (
    Status.NEVER_GRANTED,
    Status.REVERTED_LIKELY,
    Status.TERMINABLE_NOW,
    Status.TERMINABLE_FUTURE,
    Status.GRANTED_ACTIVE,
    Status.LAPSED_WINDOW,
)
TERMINAL: tuple[Status, ...] = (Status.EXCLUDED_WFH, Status.PUBLIC_DOMAIN)


def _rank(status: Status) -> int:
    """Lower is more actionable. Terminal statuses rank below the whole ladder."""
    return LADDER.index(status) if status in LADDER else len(LADDER)


@dataclass(frozen=True)
class GrantPosition:
    grant_id: str
    contribution: Contribution | None
    status: Status | None
    winner: ChannelResult | None  # the result that set the position
    constituents: tuple[ChannelResult, ...]


@dataclass(frozen=True)
class ContributionPosition:
    contribution: Contribution | None
    status: Status | None
    winner: GrantPosition | None
    constituents: tuple[GrantPosition, ...]


@dataclass(frozen=True)
class TriplePosition:
    work_id: str
    right_type: RightType
    territory: str | None
    status: Status | None
    weakest: ContributionPosition | None
    constituents: tuple[ContributionPosition, ...]

    @property
    def grants(self) -> tuple[GrantPosition, ...]:
        return tuple(g for c in self.constituents for g in c.constituents)


def grant_position(results: tuple[ChannelResult, ...]) -> GrantPosition:
    """Level 1. All results must belong to one grant."""
    grant_ids = {r.grant_id for r in results}
    if len(grant_ids) != 1 or None in grant_ids:
        raise ValueError(f"level 1 rolls up one grant; got {sorted(map(str, grant_ids))}")
    statuses = [r for r in results if isinstance(r, StatusResult)]
    terminal = [r for r in statuses if r.status in TERMINAL]
    if terminal:
        winner = terminal[0]  # terminal for the grant across every channel
    elif statuses:
        winner = min(statuses, key=lambda r: _rank(r.status))
    else:
        winner = None
    contribution = next(iter({r.contribution for r in results}))
    return GrantPosition(grant_id=results[0].grant_id, contribution=contribution,
                         status=winner.status if winner else None, winner=winner, constituents=tuple(results))


def contribution_position(grants: tuple[GrantPosition, ...]) -> ContributionPosition:
    """Level 2. All positions must share one contribution."""
    contributions = {g.contribution for g in grants}
    if len(contributions) != 1:
        raise ValueError(f"level 2 rolls up one contribution; got {sorted(map(str, contributions))}")
    with_status = [g for g in grants if g.status is not None]
    winner = min(with_status, key=lambda g: _rank(g.status)) if with_status else None
    return ContributionPosition(contribution=next(iter(contributions)), status=winner.status if winner else None,
                                winner=winner, constituents=tuple(grants))


def triple_position(work_id: str, right_type: RightType, grants: tuple[Grant, ...],
                    results: tuple[ChannelResult, ...], territory: str | None = None) -> TriplePosition:
    """Level 3, built from levels 1 and 2 over the grants that convey ``right_type``."""
    in_scope = {g.grant_id for g in grants if right_type in g.right_types}
    by_grant: dict[str, list[ChannelResult]] = {}
    for r in results:
        if r.grant_id in in_scope:
            by_grant.setdefault(r.grant_id, []).append(r)
    grant_positions = [grant_position(tuple(rs)) for rs in by_grant.values()]
    by_contribution: dict[Contribution | None, list[GrantPosition]] = {}
    for gp in grant_positions:
        by_contribution.setdefault(gp.contribution, []).append(gp)
    contributions = tuple(contribution_position(tuple(gps)) for gps in by_contribution.values())

    terminal = [c for c in contributions if c.status in TERMINAL]
    unknown = [c for c in contributions if c.status is None]
    if terminal:
        weakest = terminal[0]  # a known blocker dominates an unknown
    elif unknown or not contributions:
        weakest = unknown[0] if unknown else None
    else:
        weakest = max(contributions, key=lambda c: _rank(c.status))
    return TriplePosition(work_id=work_id, right_type=right_type, territory=territory,
                          status=weakest.status if weakest else None, weakest=weakest, constituents=contributions)
