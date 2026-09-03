# Domain Rules

## Ticket reservation

- **Hold + expiry**: reserving a ticket creates a *hold* on N seats for a fixed TTL (default 10 minutes), not an immediate confirmed booking. If payment/confirmation doesn't complete before `expires_at`, the hold is treated as released and those seats become available again.
- **No overselling (implied by hold+expiry)**: an event's confirmed bookings plus *active* (non-expired) holds must never exceed its capacity. Since a hold provisionally consumes capacity, computing "available seats" must exclude expired holds — an expired hold that's still sitting in storage does not count against capacity.
- **A hold is per-reservation-attempt, not per-user**: a user can have at most one active hold per event at a time (prevents one user parking multiple holds to grief availability). A new hold request while one is already active for the same user+event should reuse/extend it rather than stacking a second hold.
- **Confirming a hold after it has expired must fail**: payment/confirmation arriving after `expires_at` is rejected — the seats may have already been re-allocated to someone else. The user must re-request a hold.

_Update this file as new rules are discovered during pipeline runs — append, don't rewrite existing entries._
