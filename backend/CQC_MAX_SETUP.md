# CQC Max entitlement setup

Rule Mirror keeps its users, brokerage-export journals, portfolios, and
sessions in its own database. CQC Max is checked against Oryntra through an
opaque HMAC subject derived locally from the signed-in email. Raw email,
passwords, sessions, and trading records are not transmitted.

Set these values in Rule Mirror's deployment environment after configuring the
same secret in Oryntra:

```text
CQC_ENTITLEMENT_API_URL=https://oryntraai.com
CQC_ENTITLEMENT_SHARED_SECRET=<same private random value used by Oryntra>
CQC_ENTITLEMENT_TIMEOUT_SECONDS=3
```

`GET /api/v1/account/entitlement` returns the signed-in user's effective
software products. It fails closed on a missing setting, signature rejection,
or service outage. A CQC Max grant expands to `rulemirror_pro`; it does not
automatically make unrelated Rule Mirror features paid or expose other users'
information.

Before enabling a purchase, connect verified StoreKit purchase events and
renewal/revocation events to Oryntra's `cqc_entitlements` ledger, then put a
real Rule Mirror Pro-only feature behind this endpoint's `rulemirror_pro`
result.
