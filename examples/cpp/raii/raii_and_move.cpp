/**
 * Topic: RAII and move semantics in C++.
 *
 * Concepts (advanced):
 * - RAII: tie resource lifetime to object lifetime
 * - Rule of Five (why owning a resource forces extra special members)
 * - Move constructors / move assignment: transfer, don't copy
 * - std::move and std::exchange idioms
 * - std::unique_ptr as the default owning pointer
 *
 * RAII ("Resource Acquisition Is Initialization") means: acquire a
 * resource in a constructor, release it in the destructor. Scope
 * ends -> destructor runs -> resource freed. No leaks, even when
 * exceptions fly.
 *
 * Moving transfers ownership from one object to another in O(1)
 * instead of deep-copying; the source is left in a valid, empty
 * state.
 *
 * Compile:  g++ -std=c++17 -Wall -Wextra -o raII_demo raii_and_move.cpp
 *
 * NOTE: validated by inspection (no C++ toolchain on authoring host).
 */

#include <cstddef>
#include <iostream>
#include <memory>
#include <utility>
#include <vector>

/**
 * A minimal RAII wrapper around a raw file handle (int).
 *
 * The destructor ALWAYS closes the file, on every path:
 * normal return, early return, or exception.
 */
class FileHandle {
public:
    explicit FileHandle(int fd) : fd_(fd) {
        std::cout << "  [open]  fd=" << fd_ << "\n";
    }

    // Deleting the copy operations makes double-close impossible.
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;

    // Move: take the other handle, leave it closed (fd_ = -1).
    FileHandle(FileHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
        std::cout << "  [move]  fd=" << fd_ << " transferred\n";
    }

    FileHandle& operator=(FileHandle&& other) noexcept {
        if (this != &other) {
            close();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    ~FileHandle() {
        close();
    }

    void read(char* buf, std::size_t n) const {
        (void)buf;
        (void)n;
        // pretend to read fd_ bytes
    }

private:
    void close() {
        if (fd_ != -1) {
            std::cout << "  [close] fd=" << fd_ << "\n";
            fd_ = -1;
        }
    }

    int fd_;
};

/** Returns a unique_ptr that owns a FileHandle (heap-allocated RAII). */
std::unique_ptr<FileHandle> open_file(int fd) {
    return std::make_unique<FileHandle>(fd);
}

int main() {
    std::cout << "1. Basic RAII: resource freed at scope end\n";
    {
        auto file = open_file(3);
        file->read(nullptr, 16);
    }  // <- unique_ptr destroyed here -> FileHandle::~FileHandle
    std::cout;

    std::cout << "2. Exception safety: resource freed on throw\n";
    try {
        {
            auto file = open_file(4);
            file->read(nullptr, 16);
            throw std::runtime_error("boom");  // simulates a read error
        }
    } catch (const std::exception& e) {
        std::cout << "  caught: " << e.what() << "\n";
    }
    std::cout;  // (the [close] line above proves no leak)

    std::cout << "3. Moving: ownership transfer without a copy\n";
    FileHandle a(5);
    {
        FileHandle b(std::move(a));   // a's fd moves into b
        b.read(nullptr, 8);
    }  // b closes fd=5; a is empty (fd_ = -1), closes nothing
    std::cout << "  a is safely empty after the move\n";
    std::cout;

    std::cout << "4. unique_ptr in a container: batch of resources\n";
    std::vector<std::unique_ptr<FileHandle>> handles;
    handles.push_back(open_file(6));
    handles.push_back(open_file(7));
    // handles.clear(); or let it go out of scope:
    for (auto& h : handles) {
        h->read(nullptr, 4);
    }
    // vector destroyed at end of main -> both files closed, in order

    std::cout << "done\n";
}

/**
 * Expected output:
 *
 * 1. Basic RAII: resource freed at scope end
 *   [open]  fd=3
 *   [close] fd=3
 *
 * 2. Exception safety: resource freed on throw
 *   [open]  fd=4
 *   [close] fd=4
 *   caught: boom
 *
 * 3. Moving: ownership transfer without a copy
 *   [open]  fd=5
 *   [move]  fd=5 transferred
 *   [close] fd=5
 *   a is safely empty after the move
 *
 * 4. unique_ptr in a container: batch of resources
 *   [open]  fd=6
 *   [open]  fd=7
 * done
 *   [close] fd=7
 *   [close] fd=6
 */
