# Security & Cryptography

Interviewers use crypto questions to see if you can separate the three jobs
that get lumped together: **confidentiality** (encryption), **integrity and
authenticity** (hashes, MACs, signatures), and **availability** (DoS,
rate limits). Getting the labels straight is most of the answer.

---

### 🟢 Q. Symmetric vs asymmetric encryption — what's the difference and
why do we need both?

**Answer.** **Symmetric** (AES, ChaCha20) uses one shared key for encrypt
and decrypt — fast, but you must get the key to the other party safely.
**Asymmetric** (RSA, X25519) uses a public/private key pair — anyone can
encrypt with the public key, only the holder of the private key can decrypt
— which solves key distribution but is far slower.

Real systems use both: TLS does an **asymmetric** (or Diffie-Hellman) key
exchange to agree on a fresh **symmetric** session key, then bulk-encrypts
the data with the symmetric key. You get the secure key exchange of public
keys and the speed of symmetric crypto. The same split underpins signing
(sign fast with a hash, then apply the slow private key to the digest).

---

### 🟡 Q. A cryptographic hash is not a MAC. What's the difference, and
why does it matter?

**Answer.** A plain hash (SHA-256) is a **one-way fingerprint**: it has no
secret, so anyone who can see the message can recompute the digest. A
**MAC** (HMAC) additionally takes a **shared secret key**, so only someone
with the key can produce a valid tag — that's what gives it *authenticity*.

```python
import hashlib, hmac, secrets

# Plain hash: deterministic, and reproducible by ANYONE who has the message.
assert hashlib.sha256(b"password").hexdigest() == \
       hashlib.sha256(b"password").hexdigest()

# HMAC: needs the key to forge a valid tag.
key = secrets.token_bytes(32)
msg = b"transfer 100 to bob"
tag = hmac.new(key, msg, hashlib.sha256).hexdigest()
assert tag == hmac.new(key, msg, hashlib.sha256).hexdigest()          # same key, same tag
assert tag != hmac.new(key, b"transfer 200 to bob", hashlib.sha256).hexdigest()
assert hmac.compare_digest(tag, tag) and not hmac.compare_digest(tag, "x")
```

The concrete failure of `hash(secret + msg)` (a "homebrew MAC"): the
concatenation is ambiguous, so different `(secret, msg)` pairs collide.

```python
# Two different (secret, msg) splits hash to the SAME value:
a = hashlib.sha256(b"sec" + b"retmsg").hexdigest()
b = hashlib.sha256(b"secret" + b"msg").hexdigest()
assert a == b   # both are the byte string 'secretmsg' — the split is unknowable
```

HMAC's structure (keyed inner/outer hash) is designed to avoid exactly this.
Also note `hmac.compare_digest` — a **timing-safe** comparison, because a
naive `==` can leak how many leading bytes of a forger's tag were correct.

---

### 🟡 Q. How should you store user passwords?

**Answer.** Never a plain hash. Use a **slow, salted, keyed** function:
a **per-user random salt** (so identical passwords produce different
digests and rainbow tables are useless) plus a deliberately expensive
function (bcrypt, scrypt, or Argon2 — or PBKDF2 with a high iteration
count) so brute force is expensive.

```python
import hashlib, secrets

password = b"hunter2"
salt = secrets.token_bytes(16)                       # per-user, stored alongside
digest = hashlib.pbkdf2_hmac("sha256", password, salt, 600_000).hex()

# Verification re-derives with the SAME salt and compares in constant time.
import hmac
assert hmac.compare_digest(
    hashlib.pbkdf2_hmac("sha256", password, salt, 600_000).hex(), digest
)
assert not hmac.compare_digest(
    hashlib.pbkdf2_hmac("sha256", b"hunter3", salt, 600_000).hex(), digest
)
# Same password, different salt -> different digest (defeats rainbow tables).
salt2 = secrets.token_bytes(16)
assert hashlib.pbkdf2_hmac("sha256", password, salt2, 600_000).hex() != digest
```

The three properties to name: **salt** (uniqueness), **slowness/work
factor** (costs the attacker), and **you cannot reverse it** (so on breach
an attacker still has to brute-force each password individually). Store
only `salt + digest`, never the password or a reversible-encrypted form.

---

### 🟡 Q. What happens during a TLS handshake, in one paragraph?

**Answer.** The client sends a `ClientHello` with its cipher preferences
and a random; the server replies with its certificate (signed up a chain
to a trusted CA) and its own random, and the two parties run a key
exchange (ECDHE) from which both independently derive the same symmetric
session keys using the two randoms. Because the server's certificate is
verified against the CA chain, the client is confident it's talking to the
right host, and because ECDHE contributes fresh randomness, the session
keys are new each connection (giving **forward secrecy** — a later leak of
the server's private key doesn't decrypt past sessions). Only then does
encrypted application data flow, using the fast symmetric keys.

The two things interviewers probe: **authentication** (the certificate
chain answers "are you really `bank.com`?") and **forward secrecy**
(ECDHE answers "if my private key leaks next year, is today's traffic safe?").

---

### 🔴 Q. An attacker steals your database. What should have been true,
and what are they still missing?

**Answer.** Layered defence, in order of how much it helps *after* the
breach: (1) **passwords** were stored as salted slow hashes, so the dump
doesn't hand over logins — the attacker must brute-force each one; (2)
**sensitive fields** (cards, SSNs, tokens) were **encrypted at rest** with
keys held outside the database (KMS/HSM), so the dump is ciphertext
without the key; (3) **secrets** (API keys, DB credentials) were never in
the repo or the image — they live in a secrets manager; (4) access was
**least-privilege** and logged, limiting what the stolen role could reach.

The answer they want is the shift in mindset: you **cannot** assume the
database is safe, so you make a stolen database *worth less* than the cost
of attacking it. The single most-cited failure is storing passwords as a
plain or fast hash (or reversible-encrypted), which turns a DB breach into
an instant credential breach.

---

### 🟢 Q. What's the difference between a hash, a MAC, and a signature?

**Answer.**

| Tool | Secret? | Proves | Who can verify |
|---|---|---|---|
| Hash (SHA-256) | none | integrity only (accidental) | anyone |
| MAC (HMAC) | shared key | integrity + authenticity | anyone with the key |
| Signature (RSA/Ed25519) | private key | integrity + authenticity + **non-repudiation** | anyone with the public key |

A **signature** is the asymmetric upgrade of a MAC: the sender signs with a
private key, and *anyone* can verify with the public key, and the sender
can't plausibly deny it (non-repudiation). A **MAC** is symmetric — fast,
but the verifier must hold the shared secret, so it can't be publicly
verified. Use MACs for server↔server over a trusted channel, signatures for
publicly verifiable artifacts (code, containers, documents, TLS certs).
