# Networking

"What happens when you type a URL into a browser?" is the single most-asked
open-ended interview question. Everything here feeds into it.

---

### 🟢 Q. TCP vs UDP?

**Answer.**

| | TCP | UDP |
|---|---|---|
| Connection | Handshake first | None — just send |
| Delivery | Guaranteed, retransmits | Best effort, may drop |
| Ordering | Preserved | None |
| Congestion control | Yes | No |
| Header | 20+ bytes | 8 bytes |
| Speed | Slower | Faster, lower latency |

**TCP** when correctness matters: HTTP, email, file transfer, databases.
**UDP** when timeliness beats completeness: live video and voice, gaming, DNS.

The insight worth stating: for a video call, a packet that arrives late is
useless — retransmitting it would make things *worse* by delaying everything
behind it. Dropping it and carrying on is the correct behaviour. (QUIC, which
HTTP/3 runs on, is built on UDP and reimplements reliability per-stream to avoid
exactly this head-of-line blocking.)

---

### 🟡 Q. Explain the TCP three-way handshake, and why it is three.

**Answer.**

1. **SYN** — client sends its initial sequence number.
2. **SYN-ACK** — server acknowledges it and sends its own.
3. **ACK** — client acknowledges the server's.

Three steps because **both directions** must be established, and each side must
confirm the other's sequence number. Two would leave the server unsure the client
received its number.

The cost: one full round trip before any data flows. On a 100 ms link that is 100
ms before the request is even sent, plus another ~2 round trips for the TLS
handshake. This is why connection reuse (keep-alive), HTTP/2 multiplexing and
QUIC's 0-RTT resumption all exist.

Closing takes **four** steps (FIN/ACK each way), because each direction closes
independently — one side can finish sending while still receiving.

---

### 🟢 Q. What happens when you type a URL and press enter?

**Answer.** The structure matters more than the detail; go layer by layer.

1. **URL parsing** — scheme, host, port, path.
2. **DNS resolution** — browser cache → OS cache → router → resolver → root → TLD
   → authoritative nameserver, returning an IP.
3. **TCP connection** — three-way handshake to that IP on port 443.
4. **TLS handshake** — negotiate the cipher, validate the certificate chain
   against a trusted root, derive session keys.
5. **HTTP request** — `GET / HTTP/1.1` plus headers (Host, cookies, Accept).
6. **Server processing** — load balancer → application server → cache or database
   → response.
7. **Response** — status line, headers, body.
8. **Rendering** — parse HTML into the DOM, fetch CSS/JS/images (more requests,
   back to step 2), build the render tree, layout, paint.

Strong candidates then mention **caching at every layer** — DNS TTL, browser
cache, CDN, server-side cache — because the fastest request is the one never made.

---

### 🟡 Q. What is the difference between HTTP/1.1, HTTP/2 and HTTP/3?

**Answer.**

- **HTTP/1.1** — one request at a time per connection. Browsers open ~6
  connections per host to compensate. Suffers **head-of-line blocking**: a slow
  response stalls everything behind it.
- **HTTP/2** — binary framing with **multiplexing**: many concurrent streams over
  one TCP connection, plus header compression (HPACK) and server push. Fixes HTTP
  head-of-line blocking, but not TCP's — one lost packet still stalls every
  stream, because TCP must deliver bytes in order.
- **HTTP/3** — runs over **QUIC on UDP**, giving each stream independent delivery.
  A lost packet stalls only its own stream. Also merges the transport and TLS
  handshakes into one round trip.

---

### 🟡 Q. What does DNS actually do, and what is a TTL?

**Answer.** It translates a hostname into an IP address, through a hierarchy:
root servers → TLD servers (`.com`) → the domain's authoritative nameservers.

Record types worth knowing: **A** (IPv4), **AAAA** (IPv6), **CNAME** (alias),
**MX** (mail), **TXT** (verification, SPF), **NS** (delegation).

**TTL** is how long a resolver may cache a record. It is the trade-off at the
heart of DNS-based failover: a low TTL means changes propagate fast but you pay
more lookups; a high TTL is efficient but leaves stale records pointing at a dead
server for hours. Lowering the TTL *before* a planned migration is the standard
practice.

---

### 🟡 Q. What does HTTPS actually protect, and how?

**Answer.** TLS provides three things:

1. **Encryption** — an eavesdropper sees ciphertext.
2. **Integrity** — tampering is detected.
3. **Authentication** — the certificate proves you are talking to the real host.

It works by using **asymmetric** cryptography (slow) only to agree on a shared
**symmetric** key (fast), then encrypting the actual traffic symmetrically. Trust
comes from a chain: the site's certificate is signed by an intermediate CA,
signed by a root CA that your OS or browser already trusts.

Worth knowing what it does *not* hide: the destination IP, and the hostname
during the handshake (SNI is sent in clear unless Encrypted Client Hello is in
use). An observer cannot read your traffic but can see which site you visited.

---

### 🟢 Q. What do the HTTP status code classes mean?

**Answer.**

| Class | Meaning | Worth knowing |
|---|---|---|
| 1xx | Informational | 101 Switching Protocols (WebSocket upgrade) |
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirection | 301 permanent, 302 temporary, 304 Not Modified |
| 4xx | **Client** error | 400, 401 unauthenticated, 403 unauthorised, 404, 429 rate limited |
| 5xx | **Server** error | 500, 502 bad gateway, 503 unavailable, 504 timeout |

The distinction interviewers probe: **401 vs 403** — 401 means "I do not know who
you are, authenticate"; 403 means "I know who you are and you may not do this".
And **301 vs 302** — 301 is cached aggressively by browsers and is effectively
permanent, so it is hard to undo.

---

### 🟡 Q. What is the difference between a load balancer at L4 and L7?

**Answer.** **Layer 4** balances on TCP/UDP information — IP and port. It cannot
see inside the request, so it is fast and protocol-agnostic, but it can only do
simple distribution.

**Layer 7** parses the HTTP request, so it can route on path, host, headers or
cookies (`/api/*` to one pool, `/static/*` to another), terminate TLS, retry
failed requests and do sticky sessions. The cost is CPU and latency.

Use L4 for raw throughput and non-HTTP protocols; use L7 when routing decisions
depend on request content, which for a typical web application is most of the
time.
