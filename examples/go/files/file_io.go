// Topic: File I/O in Go — read, write, append, scan line by line.
//
// Concepts:
// - os.Create / os.ReadFile / os.WriteFile
// - os.Open + bufio.Scanner for line-by-line reading
// - Flag bits: os.O_APPEND, os.O_CREATE, os.O_WRONLY
// - chmod modes (0o644)
// - Error handling after EVERY OS call
// - os.Stat for existence/size checks
//
// Go's file API is small: a few functions in the os package plus
// bufio for buffered reading. Every call returns an error — check
// them all.
//
// Time Complexity: O(bytes) for full reads
//
// Run:  go run file_io.go
//
// NOTE: validated by inspection (no Go toolchain on authoring host).

package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func main() {
	// --- 1. Write a whole file at once --------------------------------------
	content := "alpha\nbeta\ngamma\n"
	err := os.WriteFile("demo_lines.txt", []byte(content), 0o644)
	if err != nil {
		fmt.Println("write failed:", err)
		return
	}
	defer os.Remove("demo_lines.txt") // cleanup when main exits

	// --- 2. Check what we wrote ---------------------------------------------
	info, err := os.Stat("demo_lines.txt")
	if err != nil {
		fmt.Println("stat failed:", err)
		return
	}
	fmt.Printf("size: %d bytes, mode: %v\n", info.Size(), info.Mode())
	// -> size: 17 bytes, mode: -rw-r--r--

	// --- 3. Read the whole file -----------------------------------------------
	all, err := os.ReadFile("demo_lines.txt")
	if err != nil {
		fmt.Println("read failed:", err)
		return
	}
	fmt.Printf("whole file: %q\n", string(all))
	// -> whole file: "alpha\nbeta\ngamma\n"

	// --- 4. Line-by-line with bufio.Scanner -------------------------------------
	// The idiomatic pattern for large files: don't load everything.
	f, err := os.Open("demo_lines.txt")
	if err != nil {
		fmt.Println("open failed:", err)
		return
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	lineNo := 0
	for scanner.Scan() {
		lineNo++
		line := scanner.Text()
		fmt.Printf("line %d: %s\n", lineNo, strings.ToUpper(line))
	}
	if err := scanner.Err(); err != nil {
		fmt.Println("scan failed:", err)
		return
	}
	// -> line 1: ALPHA
	//    line 2: BETA
	//    line 3: GAMMA

	// --- 5. Append mode: add without destroying -----------------------------------
	f2, err := os.OpenFile("demo_lines.txt",
		os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		fmt.Println("openfile failed:", err)
		return
	}
	// WriteString never loses errors: check the return count.
	if n, err := f2.WriteString("delta\n"); err != nil || n == 0 {
		fmt.Println("append failed:", err)
	}
	f2.Close()

	all, _ = os.ReadFile("demo_lines.txt")
	fmt.Printf("after append: %q\n", string(all))
	// -> after append: "alpha\nbeta\ngamma\ndelta\n"

	// --- 6. Graceful handling of missing files --------------------------------------
	_, err = os.ReadFile("does_not_exist.txt")
	fmt.Printf("missing file error: %v\n", err)
	// -> missing file error: open does_not_exist.txt: ...
	// (In real code: check errors.Is(err, os.ErrNotExist))
}
