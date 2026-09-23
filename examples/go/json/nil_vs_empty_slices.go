// Topic: nil vs empty slices at the JSON boundary.
// Concepts: both have len 0, append works on both, but JSON emits null vs [].
// Run: go run nil_vs_empty_slices.go
// NOTE: validated by inspection (no Go toolchain on this host).
// Expected output:
// nil: {"items":null}
// empty: {"items":[]}
// omitted: {}

package main

import (
	"encoding/json"
	"fmt"
)

type Payload struct {
	Items []string `json:"items"`
}

type OptionalPayload struct {
	Items []string `json:"items,omitempty"`
}

func mustJSON(value any) string {
	data, err := json.Marshal(value)
	if err != nil {
		panic(err)
	}
	return string(data)
}

func main() {
	var nilItems []string
	emptyItems := make([]string, 0)

	if len(nilItems) != 0 || len(emptyItems) != 0 {
		panic("both slices should be logically empty")
	}

	nilJSON := mustJSON(Payload{Items: nilItems})
	emptyJSON := mustJSON(Payload{Items: emptyItems})
	omittedJSON := mustJSON(OptionalPayload{Items: emptyItems})

	fmt.Println("nil:", nilJSON)
	fmt.Println("empty:", emptyJSON)
	fmt.Println("omitted:", omittedJSON)

	// append accepts a nil slice; no special initialization is necessary.
	nilItems = append(nilItems, "ready")
	if nilItems[0] != "ready" {
		panic("append failed")
	}
}
