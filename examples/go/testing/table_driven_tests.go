// Topic: Table-driven tests - Go's dominant testing idiom.
//
// Go ships its test runner in the standard library, and the community
// converged on one pattern: define a SLICE of cases, then loop over it. One
// test function covers a dozen scenarios, each reported independently.
//
// This file is deliberately a normal program rather than a _test.go file, so
// it runs with `go run` and you can read the assertions happening. The real
// test file it mirrors is shown at the bottom, and that is what you would
// actually write.
//
// Concepts:
// - The table: []struct{ name string; in ...; want ... }
// - t.Run for subtests, so failures name the case that broke
// - t.Errorf (continue) vs t.Fatalf (stop this test now)
// - got/want ordering in failure messages, by convention
// - Testing error cases in the same table with a wantErr field
// - Why the loop variable capture bug disappeared in Go 1.22
//
// Run: go run examples/go/testing/table_driven_tests.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import (
	"errors"
	"fmt"
	"strings"
)

// ---------------------------------------------------------------------------
// The code under test
// ---------------------------------------------------------------------------

var ErrEmpty = errors.New("empty input")

// ParseTags turns "a, b ,, c" into ["a", "b", "c"]: split, trim, drop blanks.
func ParseTags(raw string) ([]string, error) {
	if strings.TrimSpace(raw) == "" {
		return nil, ErrEmpty
	}

	var tags []string
	for _, part := range strings.Split(raw, ",") {
		trimmed := strings.TrimSpace(part)
		if trimmed != "" {
			tags = append(tags, trimmed)
		}
	}

	if len(tags) == 0 {
		return nil, ErrEmpty
	}
	return tags, nil
}

// ---------------------------------------------------------------------------
// The table
// ---------------------------------------------------------------------------

// Naming each case is the point: a failure says which SCENARIO broke, not
// just "case 3". Keep the name short and descriptive.
type parseCase struct {
	name    string
	input   string
	want    []string
	wantErr error
}

var parseCases = []parseCase{
	{
		name:  "simple list",
		input: "alpha,beta,gamma",
		want:  []string{"alpha", "beta", "gamma"},
	},
	{
		name:  "trims surrounding spaces",
		input: "  alpha ,  beta  ",
		want:  []string{"alpha", "beta"},
	},
	{
		name:  "drops empty fields",
		input: "alpha,,beta,",
		want:  []string{"alpha", "beta"},
	},
	{
		name:  "single value",
		input: "solo",
		want:  []string{"solo"},
	},
	{
		name:    "empty string",
		input:   "",
		wantErr: ErrEmpty,
	},
	{
		name:    "only whitespace",
		input:   "   ",
		wantErr: ErrEmpty,
	},
	{
		name:    "only separators",
		input:   ",,,",
		wantErr: ErrEmpty,
	},
}

// equal compares two string slices. In a real test you would reach for
// reflect.DeepEqual or google/go-cmp instead of writing this.
func equal(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func main() {
	fmt.Println("-- running the table --")

	passed, failed := 0, 0
	for _, tc := range parseCases {
		got, err := ParseTags(tc.input)

		switch {
		case tc.wantErr != nil:
			// errors.Is compares through a wrapped chain, which == does not.
			if !errors.Is(err, tc.wantErr) {
				fmt.Printf("  FAIL %-24s got err %v, want %v\n", tc.name, err, tc.wantErr)
				failed++
				continue
			}
		case err != nil:
			fmt.Printf("  FAIL %-24s unexpected error: %v\n", tc.name, err)
			failed++
			continue
		case !equal(got, tc.want):
			// Convention: report GOT first, then WANT. Consistency here makes
			// failure output scannable across a whole codebase.
			fmt.Printf("  FAIL %-24s got %v, want %v\n", tc.name, got, tc.want)
			failed++
			continue
		}

		fmt.Printf("  ok   %-24s %q -> %v\n", tc.name, tc.input, got)
		passed++
	}

	fmt.Printf("\n  %d passed, %d failed, %d total\n", passed, failed, len(parseCases))

	fmt.Println("\n-- what the real _test.go file looks like --")
	fmt.Println(testFileSource)
}

// The genuine article. Save as parse_test.go beside the code and run
// `go test ./... -v`.
const testFileSource = `package tags

import (
	"errors"
	"reflect"
	"testing"
)

func TestParseTags(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		want    []string
		wantErr error
	}{
		{name: "simple list", input: "alpha,beta", want: []string{"alpha", "beta"}},
		{name: "drops empty fields", input: "alpha,,beta,", want: []string{"alpha", "beta"}},
		{name: "empty string", input: "", wantErr: ErrEmpty},
	}

	for _, tt := range tests {
		// t.Run creates a SUBTEST. Failures are reported as
		// TestParseTags/simple_list, and you can run one with
		//     go test -run 'TestParseTags/drops_empty_fields'
		t.Run(tt.name, func(t *testing.T) {
			got, err := ParseTags(tt.input)

			if tt.wantErr != nil {
				if !errors.Is(err, tt.wantErr) {
					t.Fatalf("got error %v, want %v", err, tt.wantErr)
				}
				return
			}
			if err != nil {
				// Fatalf stops THIS subtest; Errorf would record the failure
				// and carry on, which would then panic on a nil result.
				t.Fatalf("unexpected error: %v", err)
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("got %v, want %v", got, tt.want)
			}
		})
	}
}

// Before Go 1.22 the loop variable was reused across iterations, so a
// parallel subtest capturing tt saw the LAST case. Everyone wrote
//     tt := tt
// to shadow it. Go 1.22 gives each iteration its own variable, so that
// line is no longer needed.
func TestParseTagsParallel(t *testing.T) {
	for _, tt := range []struct{ name, input string }{
		{"a", "x"}, {"b", "y"},
	} {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			if _, err := ParseTags(tt.input); err != nil {
				t.Errorf("unexpected error: %v", err)
			}
		})
	}
}
`

/* Expected output:
-- running the table --
  ok   simple list              "alpha,beta,gamma" -> [alpha beta gamma]
  ok   trims surrounding spaces "  alpha ,  beta  " -> [alpha beta]
  ok   drops empty fields       "alpha,,beta," -> [alpha beta]
  ok   single value             "solo" -> [solo]
  ok   empty string             "" -> []
  ok   only whitespace          "   " -> []
  ok   only separators          ",,," -> []

  7 passed, 0 failed, 7 total

-- what the real _test.go file looks like --
  (the source of parse_test.go, printed verbatim)
*/
