// Worker pools bound concurrency instead of starting an unbounded goroutine per job.
package main

import (
	"fmt"
	"sync"
	"time"
)

type Job struct {
	ID    int
	Value int
}

type Result struct {
	JobID  int
	Square int
}

func worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	for job := range jobs {
		time.Sleep(20 * time.Millisecond) // stand-in for I/O or CPU work
		fmt.Printf("worker %d processed job %d\n", id, job.ID)
		results <- Result{JobID: job.ID, Square: job.Value * job.Value}
	}
}

func main() {
	jobs := make(chan Job)
	results := make(chan Result)

	var workers sync.WaitGroup
	for id := 1; id <= 3; id++ {
		workers.Add(1)
		go worker(id, jobs, results, &workers)
	}

	go func() {
		for id, value := range []int{2, 4, 6, 8, 10} {
			jobs <- Job{ID: id + 1, Value: value}
		}
		close(jobs) // workers stop after all queued jobs are received
	}()

	go func() {
		workers.Wait()
		close(results) // the receiver can safely finish its range loop
	}()

	for result := range results {
		fmt.Printf("job %d result: %d\n", result.JobID, result.Square)
	}
}
