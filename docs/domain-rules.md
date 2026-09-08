# Domain Rules

## Ticket reservation

- **Hold + expiry**: reserving a ticket creates a *hold* on N seats for a fixed TTL (default 10 minutes), not an immediate confirmed booking. If payment/confirmation doesn't complete before `expires_at`, the hold is treated as released and those seats become available again.
- **No overselling (implied by hold+expiry)**: an event's confirmed bookings plus *active* (non-expired) holds must never exceed its capacity. Since a hold provisionally consumes capacity, computing "available seats" must exclude expired holds — an expired hold that's still sitting in storage does not count against capacity.
- **A hold is per-reservation-attempt, not per-user**: a user can have at most one active hold per event at a time (prevents one user parking multiple holds to grief availability). A new hold request while one is already active for the same user+event should reuse/extend it rather than stacking a second hold.
- **Confirming a hold after it has expired must fail**: payment/confirmation arriving after `expires_at` is rejected — the seats may have already been re-allocated to someone else. The user must re-request a hold.

## Provenance note: "Ticket reservation" section above

- The "Ticket reservation" rules above (hold+expiry, capacity, per-user hold reuse) and `docs/architecture.md`'s "Reservation expiry mechanism" section were committed in this repo's very first commit ("first comit", 5ea1556), landing in the same commit as the actual Passenger implementation (`app/api/passengers.py`, `app/services/passenger_service.py`, etc.) and the one Passenger migration. There has never been any `Event`/`Reservation`/`Hold`/capacity code, migration, or test in `app/`, `migrations/`, or `tests/` on **any** branch (checked: main, TRV, TRV-1, Travel, Travel-123, feature/TRV-1-travel-booking, origin/TRV-1) at any point in history — `git log --follow -p` and `git ls-tree` on every branch confirm this. `docs/architecture.md` itself frames `events`/`reservations` as illustrative examples of resource naming ("one module per resource (e.g. `events`, `reservations`)"), not a commitment. Conclusion: this content is template/scaffold boilerplate describing a hypothetical example domain, unconnected to any code ever built here (including Passenger and Booking/Trip) — treat it as illustrative only, not as a spec that Booking/Trip (or any other resource) must implement, unless a future requirement explicitly asks for event capacity/holds.

## Passenger resource (from app/db/models.py, app/services/passenger_service.py)

- A Passenger's identity/uniqueness key is the `(government_id_type, government_id_number)` pair, not name or email — see `uq_passenger_government_id` constraint (`app/db/models.py:18-24`) and `PassengerAlreadyExistsError` (`app/services/passenger_service.py:15-20`). Two passengers may legitimately share a full name; don't dedupe or key lookups on name.
- No `404`/not-found error shape is established anywhere in the codebase yet (only the `409` duplicate-resource shape from `docs/conventions.md` has a real precedent — `app/api/passengers.py:30-37`). Any new endpoint that needs to report "referenced resource not found" (e.g. a Booking referencing a nonexistent Passenger/Trip id) is the first to need this and has no existing pattern to copy.

_Update this file as new rules are discovered during pipeline runs — append, don't rewrite existing entries._
