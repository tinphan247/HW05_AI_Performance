# Group scope confirmation — HW05

**Student:** Phan Trung Tin — 23120372  
**Date:** 2026-11-16

## Selected workflow

End-to-end workflow covering all three required endpoint groups:

1. `POST /api/login` — auth-heavy
2. `GET /api/products` — read-heavy
3. `GET /api/products?search=...` — read-heavy
4. `GET /api/products/{id}` — read-heavy
5. `POST /api/cart` — transactional
6. `POST /api/checkout` — transactional
7. `GET /api/orders/my-orders` — transactional read
8. Lockout probe: `POST /api/login` with wrong password ×3 — auth-heavy negative check

## Duplicate check

- The student answered **“không”** when asked whether this workflow is duplicated with another group member.
- **Member list and their workflows are still to be recorded here.** Do not claim “no duplication” in the final report until this table is complete and, ideally, supported by a group chat screenshot or signed confirmation.

| Member | Student ID | Selected workflow | Confirmed non-duplicate? |
|---|---|---|---|
| Phan Trung Tin | 23120372 | Login + product browse/search + cart + checkout + my-orders | — |
| TBD | TBD | TBD | TBD |

## Evidence to attach

- [ ] Group chat screenshot / meeting note
- [ ] Date and time of confirmation
- [ ] Final member/workflow table
