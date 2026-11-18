# Scope confirmation - HW05

**Student:** Phan Trung Tin - 23120372
**Date:** 2026-11-16 (updated 2026-11-18)

## Assignment mode

This submission is **individual**. There is no group member list, no shared workflow and no
cross-member duplicate comparison. No names, student IDs or confirmations of other students are
included, because inventing them would be false evidence.

If the course requires a cross-student table, this file is the honest record: there are no
additional members to list for this submission.

## Selected workflow

End-to-end workflow covering all three required endpoint groups:

1. `POST /api/login` - auth-heavy
2. `GET /api/products` - read-heavy
3. `GET /api/products?search=...` - read-heavy
4. `GET /api/products/{id}` - read-heavy
5. `POST /api/cart` - transactional
6. `POST /api/checkout` - transactional
7. `GET /api/orders/my-orders` - transactional read
8. Lockout probe: `POST /api/login` with wrong password x3 - auth-heavy negative check

The workflow is defined once in `scripts/generate_jmx.py` and reused by all five plans
(Load, Stress, Spike, Endurance, Lockout) so the scenarios are directly comparable.

## Duplicate check

- The workflow above is used **only** by this individual submission.
- No group chat screenshot, meeting note or signed confirmation exists for a group, and none is
  fabricated.

| Member | Student ID | Selected workflow | Confirmed non-duplicate? |
|---|---|---|---|
| Phan Trung Tin | 23120372 | Login + product browse/search + cart + checkout + my-orders | Individual submission - no peer workflow to compare |
