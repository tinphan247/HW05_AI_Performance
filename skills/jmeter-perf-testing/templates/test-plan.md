# Test plan — <scenario>

- **Student / author:**
- **Date:**
- **SUT:** <repo URL> @ `<commit>`
- **Base URL / port:** `http://localhost:<port>` (<note any port patch>)
- **Dataset:** `<csv path>` (SHA-256 `<hash>`), users `<n>`, products `<n>`, orders `<n>`
- **Tool:** Apache JMeter `<version>`, JDK `<version>`

## Shared workflow

| # | Request | Group | Assertion |
|---|---|---|---|
| 1 | `GET /api/products` | read | 200 + body contains `"name"` |
| 2 | `GET /api/products?search=${search_keyword}` | read | 200 |
| 3 | `POST /api/login` | auth | 200 + body contains `"token"`, extract `$.token` |
| 4 | `GET /api/products/${product_id}` | read | 200 + body contains `"id"` |
| 5 | `POST /api/cart` | transactional | 200 + `Added to cart` |
| 6 | `POST /api/checkout` | transactional | 200 + body contains `"orderId"` |
| 7 | `GET /api/orders/my-orders` | transactional read | 200 |

## Load shape

| Parameter | Value | Reason |
|---|---|---|
| Threads | | |
| Ramp-up | | |
| Duration | | |
| Think time | | |
| Loop | forever + scheduler | |
| Stop condition | | |

## Report view

- Primary:
- Screenshot method (from saved JTL, not live):
- HTML dashboard path:

## Risks / validity threats

- Same host for JMeter and backend?
- SQLite vs production DB?
- In-memory cart?
- Dataset size?
- Other processes?

## Evidence paths

- JTL:
- HTML:
- Resource CSV:
- Manifest:
- Analysis:
