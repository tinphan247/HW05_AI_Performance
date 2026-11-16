# Local port patch — EShop backend

**Reason:** the student already runs another backend (Aptis) on port 3000, so the EShop SUT must listen on a different port.

## Change

File: `sut/eshop-sut/backend/server.js`

```diff
-const PORT = 3000;
+const PORT = process.env.PORT || 3100;
```

`PORT` can also be overridden explicitly:

```powershell
$env:PORT = "3100"
node server.js
```

## Scope and honesty

- This is a **local test-harness port change only**; no business logic was modified.
- The official SUT default is still 3000. The final report must state that the test environment used **3100** to coexist with the Aptis backend.
- All test plans, scripts, and documentation must use **3100**, not 3000.
- The SUT clone is git-ignored; the patch is documented here and can be reproduced with the diff above.

## Verification

```text
GET http://localhost:3100/api/products -> HTTP 200
```
