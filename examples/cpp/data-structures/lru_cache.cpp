/**
 * Topic: LRU (Least Recently Used) cache.
 *
 * Concepts (advanced):
 * - Combining data structures: doubly linked list + hash map
 * - Amortized O(1) cache operations
 * - Iterator indirection instead of raw pointers
 * - std::list::splice for O(1) reordering without allocation
 *
 * The cache stores at most `capacity` key/value pairs. On `get` or
 * `put`, the accessed key becomes "most recently used". When the
 * cache is full and a new key is inserted, the least recently used
 * key is evicted.
 *
 * Both get() and put() run in O(1) average time:
 *   - unordered_map  -> O(1) lookup of a key's list node
 *   - std::list      -> O(1) move-to-front / pop-from-back
 *
 * NOTE: No C++ toolchain was available on the authoring machine,
 * so this file was reviewed by inspection. It targets C++17.
 */

#include <cstddef>
#include <iostream>
#include <list>
#include <optional>
#include <string>
#include <unordered_map>

class LRUCache {
public:
    explicit LRUCache(std::size_t capacity) : capacity_(capacity) {}

    /** Returns the value for `key`, marking it most-recently-used. */
    std::optional<int> get(const std::string& key) {
        auto it = index_.find(key);
        if (it == index_.end()) {
            return std::nullopt;          // cache miss
        }
        // Move the node to the front (most recently used position).
        entries_.splice(entries_.begin(), entries_, it->second);
        return it->second->second;
    }

    /**
     * Inserts or updates `key`. If the cache is at capacity and the
     * key is new, the least recently used entry is evicted first.
     */
    void put(const std::string& key, int value) {
        auto it = index_.find(key);
        if (it != index_.end()) {
            // Key exists: update value and mark as most recent.
            it->second->second = value;
            entries_.splice(entries_.begin(), entries_, it->second);
            return;
        }

        if (entries_.size() == capacity_) {
            // Evict the least recently used entry (back of the list).
            const std::string& lru_key = entries_.back().first;
            entries_.pop_back();
            index_.erase(lru_key);
        }

        // New entries go to the front; remember the node's iterator.
        entries_.emplace_front(key, value);
        index_[key] = entries_.begin();
    }

    std::size_t size() const { return entries_.size(); }

private:
    std::size_t capacity_;

    // Front = most recently used, back = least recently used.
    std::list<std::pair<std::string, int>> entries_;

    // Maps each key to its node so lookups are O(1).
    std::unordered_map<std::string,
                       std::list<std::pair<std::string, int>>::iterator>
        index_;
};

// --- Demo -----------------------------------------------------------------

int main() {
    LRUCache cache(2);   // holds at most 2 entries

    cache.put("a", 1);
    cache.put("b", 2);
    std::cout << "get(a) = " << cache.get("a").value_or(-1) << "\n";
    // "a" is now most recent, so "b" is the eviction candidate.

    cache.put("c", 3);   // evicts "b"
    std::cout << "get(b) = " << cache.get("b").value_or(-1) << " (evicted)\n";

    cache.put("a", 10);  // updates existing key
    std::cout << "get(a) = " << cache.get("a").value_or(-1) << "\n";

    cache.put("d", 4);   // evicts "c" (last used before "a")
    std::cout << "get(c) = " << cache.get("c").value_or(-1) << " (evicted)\n";

    std::cout << "get(d) = " << cache.get("d").value_or(-1) << "\n";
    std::cout << "size   = " << cache.size() << "\n";

    // Expected output:
    // get(a) = 1
    // get(b) = -1 (evicted)
    // get(a) = 10
    // get(c) = -1 (evicted)
    // get(d) = 4
    // size   = 2
    return 0;
}
