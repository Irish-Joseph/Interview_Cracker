# Topic: Ruby hashes and arrays — the everyday idioms.
#
# Concepts:
# - Hash syntax: {key: value}, symbol vs string keys
# - Default values: Hash.new(default) and []= defaults
# - each_pair, fetch, key?, delete
# - Array: push/<<, concat, include?, zip, flatten
# - Splat (*) and double-splat (**) in method calls
# - Shorthand: hash rocket vs symbol keys, array %w[]
#
# Ruby's hashes are ordered (since 1.8) and extremely ergonomic —
# most "options" APIs and most data shaping revolves around them.
#
# Run:  ruby hash_array_idioms.rb
#
# NOTE: validated by inspection (no Ruby runtime on authoring host).

# --- 1. Hash creation and access -------------------------------------------

user = {
  name: "Alice",
  age: 30,
  "role": "admin",   # string key, coexisting with symbol keys
}

puts user[:name]          # -> Alice
puts user["role"]         # -> admin
puts user[:missing]       # -> (nothing printed; nil)

# fetch: a safer read with a default (or a lazy default).
puts user.fetch(:email, "no email")      # -> no email
puts user.fetch(:age) { |k| "no #{k}" }  # -> 30 (key exists)

puts user.key?(:name)       # -> true
puts user.key?(:nickname)   # -> false

# --- 2. Default values --------------------------------------------------------

# Option A: a constant default for missing keys.
freq = Hash.new(0)
%w[go rust go go ruby].each { |w| freq[w] += 1 }
puts "go appears #{freq["go"]} times, python appears #{freq["python"]} times"
# -> go appears 3 times, python appears 0 times   (0, not nil!)

# Option B: a block default — computed per missing key.
words = Hash.new { |hash, key| hash[key] = [] }
[["eng", "alice"], ["eng", "bob"], ["sales", "carol"]].each do |dept, person|
  words[dept] << person   # missing key -> fresh [] from the block
end
puts "eng: #{words['eng'].join(', ')}"   # -> eng: alice, bob

# --- 3. Updating hashes ----------------------------------------------------------

user[:age] += 1            # -> 31
user[:city] = "Berlin"     # add new key
removed = user.delete("role")   # remove the STRING key
puts "removed: #{removed}"       # -> removed: admin

puts user.inspect
# -> {name: "Alice", age: 31, city: "Berlin"}

# merge: non-destructive (returns new) vs destructive (mutates)
base = { a: 1, b: 2 }
extra = { b: 20, c: 30 }
puts (base.merge(extra)).inspect   # -> {a: 1, b: 20, c: 30} (base untouched)
base.merge!(extra)
puts base.inspect                  # -> {a: 1, b: 20, c: 30} (base mutated)

# --- 4. Array idioms ----------------------------------------------------------------

nums = [1, 2, 3]
nums.push(4)      # or: nums << 4
nums.concat([5, 6])
puts nums.inspect # -> [1, 2, 3, 4, 5, 6]

puts nums.include?(3)   # -> true
puts nums.include?(99)  # -> false

# zip: pairwise combination (like Python's zip)
letters = %w[a b c]
pairs = letters.zip(nums)
puts pairs.inspect
# -> [["a", 1], ["b", 2], ["c", 3]]

# flatten: collapse nested arrays
nested = [1, [2, [3, 4]], 5]
puts nested.flatten.inspect    # -> [1, 2, 3, 4, 5]
puts nested.flatten(1).inspect # -> [1, 2, [3, 4], 5]  (only one level)

# --- 5. Splat: spreading -------------------------------------------------------------

def sum_all(*values)         # collect all args into an array
  values.sum
end

puts sum_all(1, 2, 3)        # -> 6
array = [10, 20]
puts sum_all(*array)         # -> 30 (spread the array)

# Double splat for hashes:
def show_opts(opts = {})
  puts "name=#{opts[:name] || "-"} verbose=#{!!opts[:verbose]}"
end

settings = { name: "cli", verbose: true, timeout: 30 }
show_opts(**settings)        # -> name=cli verbose=true
# (timeout is accepted but unused by show_opts)

# --- 6. %w[] and %i[]: quick literals ---------------------------------------------------

days = %w[mon tue wed thu fri]
puts days.inspect            # -> ["mon", "tue", "wed", "thu", "fri"]
symbols = %i[:a :b :c].map { |s| s.to_sym }
puts symbols.inspect         # -> [:a, :b, :c]
