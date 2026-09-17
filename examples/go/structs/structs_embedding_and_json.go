// Topic: Structs, embedding, and JSON tags.
//
// Go has no inheritance. It has EMBEDDING: put a type inside a struct without
// a field name, and its fields and methods are promoted to the outer type.
// That gives you composition with convenient access, but it is not an
// is-a relationship -- the outer type does not substitute for the inner one.
//
// Concepts:
// - Struct literals, zero values, and pointer vs value receivers
// - Embedding, promotion, and shadowing an embedded field
// - Struct tags: json:"name,omitempty" and json:"-"
// - Why exported (capitalised) fields are required for encoding/json
// - Unmarshalling, and distinguishing "absent" from "zero" with a pointer
//
// Run: go run examples/go/structs/structs_embedding_and_json.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"
)

// ---------------------------------------------------------------------------
// 1. A plain struct with tags
// ---------------------------------------------------------------------------

// Only EXPORTED fields are visible to encoding/json. A lowercase field is
// invisible to the encoder no matter what tag you give it.
type Address struct {
	Street string `json:"street"`
	City   string `json:"city"`
	// omitempty drops the field when it holds the zero value.
	Postcode string `json:"postcode,omitempty"`
	// "-" excludes the field entirely, in both directions.
	Internal string `json:"-"`
}

// ---------------------------------------------------------------------------
// 2. Embedding
// ---------------------------------------------------------------------------

type Timestamps struct {
	CreatedAt time.Time `json:"created_at"`
	// CAREFUL: omitempty does NOT omit a zero time.Time. It only treats
	// false, 0, a nil pointer/interface, and an empty string/slice/map/array
	// as empty -- never a struct. A zero time still encodes as
	// "0001-01-01T00:00:00Z". Use *time.Time if you need it to disappear.
	UpdatedAt time.Time `json:"updated_at,omitempty"`
}

// Touch has a POINTER receiver because it mutates.
func (t *Timestamps) Touch(at time.Time) {
	t.UpdatedAt = at
}

// Age has a VALUE receiver because it only reads.
func (t Timestamps) Age(now time.Time) time.Duration {
	return now.Sub(t.CreatedAt)
}

type User struct {
	Timestamps // embedded: no field name

	ID    int      `json:"id"`
	Name  string   `json:"name"`
	Email string   `json:"email,omitempty"`
	Tags  []string `json:"tags,omitempty"`

	// A named (non-embedded) struct field nests in the JSON.
	Address Address `json:"address"`

	// A POINTER lets you tell "field absent" from "field present and zero".
	Verified *bool `json:"verified,omitempty"`
}

// String gives User a custom text form. Note it does NOT affect JSON.
func (u User) String() string {
	return fmt.Sprintf("User(%d, %s)", u.ID, u.Name)
}

// ---------------------------------------------------------------------------
// 3. Shadowing an embedded field
// ---------------------------------------------------------------------------

type Audited struct {
	Timestamps
	// This CreatedAt shadows the promoted one. The embedded field is still
	// reachable, but only via its type name: a.Timestamps.CreatedAt
	CreatedAt string `json:"created_at"`
}

func main() {
	now := time.Date(2026, 9, 18, 10, 30, 0, 0, time.UTC)
	verified := true

	user := User{
		Timestamps: Timestamps{CreatedAt: now.Add(-48 * time.Hour)},
		ID:         7,
		Name:       "Ada Lovelace",
		Tags:       []string{"admin", "beta"},
		Address: Address{
			Street:   "12 Analytical Way",
			City:     "London",
			Internal: "never serialised",
		},
		Verified: &verified,
	}

	// Promotion: CreatedAt and Touch belong to Timestamps, but are reachable
	// directly on User -- no user.Timestamps.CreatedAt needed.
	fmt.Println("-- promotion --")
	fmt.Println("  created:", user.CreatedAt.Format(time.RFC3339))
	user.Touch(now) // promoted pointer-receiver method; user is addressable
	fmt.Println("  updated:", user.UpdatedAt.Format(time.RFC3339))
	fmt.Println("  age:    ", user.Age(now))
	fmt.Println("  String():", user)

	fmt.Println("-- marshal --")
	encoded, err := json.MarshalIndent(user, "  ", "  ")
	if err != nil {
		fmt.Println("marshal failed:", err)
		return
	}
	fmt.Println(" ", string(encoded))
	// Note: Email and Postcode are absent (omitempty + zero value).
	// Internal is absent (json:"-"). The embedded Timestamps fields are
	// FLATTENED into the top level, which is the main reason to embed.

	fmt.Println("-- unmarshal --")
	incoming := `{
	  "id": 9,
	  "name": "Grace Hopper",
	  "address": {"street": "1 Navy Yard", "city": "Arlington"},
	  "created_at": "2026-01-01T00:00:00Z",
	  "unknown_field": "ignored silently"
	}`

	var decoded User
	if err := json.Unmarshal([]byte(incoming), &decoded); err != nil {
		fmt.Println("unmarshal failed:", err)
		return
	}
	fmt.Println("  decoded:", decoded)
	fmt.Println("  city:   ", decoded.Address.City)
	fmt.Println("  created:", decoded.CreatedAt.Format(time.RFC3339))
	// Unknown JSON keys are ignored by default. Use a json.Decoder with
	// DisallowUnknownFields() if you want them to be an error instead.

	fmt.Println("-- absent vs zero --")
	// Verified is a *bool, so nil means "the key was not in the JSON",
	// which is different from the key being present and false.
	fmt.Println("  Verified is nil (absent):", decoded.Verified == nil)
	var explicitFalse User
	_ = json.Unmarshal([]byte(`{"verified": false}`), &explicitFalse)
	fmt.Println("  present-and-false:      ", explicitFalse.Verified != nil &&
		!*explicitFalse.Verified)

	fmt.Println("-- shadowing --")
	audited := Audited{
		Timestamps: Timestamps{CreatedAt: now},
		CreatedAt:  "2026-09-18 (as text)",
	}
	fmt.Println("  outer  audited.CreatedAt:           ", audited.CreatedAt)
	fmt.Println("  inner  audited.Timestamps.CreatedAt:", audited.Timestamps.CreatedAt.Format(time.RFC3339))
	// Marshalling Audited emits the OUTER CreatedAt; the shadowed one is
	// dropped because both map to the same JSON key at different depths.
	shadowed, _ := json.Marshal(audited)
	fmt.Println("  json:", string(shadowed))

	fmt.Println("-- zero values --")
	var empty User
	fmt.Println("  zero struct:", empty)
	fmt.Println("  nil slice len:", len(empty.Tags), "| nil-safe:", empty.Tags == nil)
	blank, _ := json.Marshal(empty)
	fmt.Println("  json:", strings.ReplaceAll(string(blank), ",", ", "))
}

/* Expected output (JSON indentation abbreviated):
-- promotion --
  created: 2026-09-16T10:30:00Z
  updated: 2026-09-18T10:30:00Z
  age:     48h0m0s
  String(): User(7, Ada Lovelace)
-- marshal --
  MarshalIndent output containing, at the TOP level (embedded fields are
  flattened, not nested under "Timestamps"):
      created_at, updated_at, id, name, tags, address, verified
  and NOT containing:
      email     (omitempty, zero)
      postcode  (omitempty, zero)
      Internal  (json:"-")
-- unmarshal --
  decoded: User(9, Grace Hopper)
  city:    Arlington
  created: 2026-01-01T00:00:00Z
-- absent vs zero --
  Verified is nil (absent): true
  present-and-false:       true
-- shadowing --
  outer  audited.CreatedAt:            2026-09-18 (as text)
  inner  audited.Timestamps.CreatedAt: 2026-09-18T10:30:00Z
  json: {"created_at":"2026-09-18 (as text)"}
-- zero values --
  zero struct: User(0, )
  nil slice len: 0 | nil-safe: true
  json: note that updated_at IS present as "0001-01-01T00:00:00Z",
        because omitempty cannot omit a struct -- see the comment on
        Timestamps above.
*/
