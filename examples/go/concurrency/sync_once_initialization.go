// Topic: Exactly-once initialization with sync.Once.
// Concepts: concurrent callers, happens-before visibility, panic semantics.
// Run: go run sync_once_initialization.go
// NOTE: validated by inspection (no Go toolchain on this host).

package main

import (
	"fmt"
	"sync"
)

var (
	loadOnce sync.Once
	config   map[string]string
	loads    int
)

func loadConfig() map[string]string {
	loadOnce.Do(func() {
		loads++
		config = map[string]string{"mode": "production"}
	})
	return config
}

func main() {
	const workers = 20
	var wait sync.WaitGroup
	wait.Add(workers)

	for i := 0; i < workers; i++ {
		go func() {
			defer wait.Done()
			if loadConfig()["mode"] != "production" {
				panic("partially initialized config")
			}
		}()
	}

	wait.Wait()
	if loads != 1 {
		panic("initializer ran more than once")
	}
	fmt.Println("loads:", loads, "mode:", config["mode"])

	// If the function passed to Do panics, Once still counts it as done. Use a
	// retry loop or cache an error when initialization is allowed to fail.
}
