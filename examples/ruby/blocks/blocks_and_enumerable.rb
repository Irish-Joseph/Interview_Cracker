# Topic: Blocks and Enumerable methods in Ruby.
#
# Concepts:
# - Blocks: the basic "code to run later" unit (do...end / {})
# - yield inside methods that take blocks
# - Enumerable: map, select, reject, each_with_object, reduce
# - Symbol-to-proc shorthand (&:)
# - Chaining Enumerable pipelines
# - each vs map vs select semantics (each returns the receiver!)
#
# Ruby's philosophy: loops are rare; you *map* and *select* over
# collections with blocks. Enumerable mixes the same methods into
# Array, Range, File, and most collection types.
#
# Run:  ruby blocks_and_enumerable.rb
#
# NOTE: validated by inspection (no Ruby runtime on authoring host).

# --- 1. yield: a method that controls the block -------------------------

def around(label)
  puts ">> #{label}"
  yield            # run whatever the caller passed
  puts "<< done"
end

around("greeting") do
  puts "hello from inside the block"
end
# ->
# >> greeting
# hello from inside the block
# << done

# Passing a value INTO the block:
def three_times(n)
  3.times { yield n }
end

three_times(4) { |v| puts "value: #{v}" }
# -> value: 4 (three times)

# --- 2. map: transform every element -------------------------------------

numbers = [1, 2, 3, 4, 5, 6]

squares = numbers.map { |n| n * n }
puts "squares:  #{squares.inspect}"
# -> [1, 4, 9, 16, 25, 36]

doubled = numbers.map(&:itself).map { |n| n * 2 }
puts "doubled:  #{doubled.first} ... (map is lazy per-element, not lazy overall)"
# map returns a NEW array; the original is unchanged.
puts "original: #{numbers.inspect}"

# --- 3. select / reject: filter elements ----------------------------------

evens = numbers.select { |n| n.even? }     # a.k.a. numbers.filter
odds  = numbers.reject { |n| n.even? }
puts "evens: #{evens.inspect}"   # -> [2, 4, 6]
puts "odds:  #{odds.inspect}"    # -> [1, 3, 5]

# --- 4. reduce/inject: fold to a single value ------------------------------

sum = numbers.reduce(0) { |acc, n| acc + n }
puts "sum: #{sum}"               # -> 21

# Building a hash in one pass with each_with_object (accumulator style):
by_parity = numbers.each_with_object(Even: [], Odd: []) do |n, acc|
  acc[n.even? ? :Even : :Odd] << n
end
puts "grouped: #{by_parity.inspect}"
# -> {:Even=>[2,4,6], :Odd=>[1,3,5]}

# --- 5. Chaining: a full pipeline ------------------------------------------

words = %w[the quick brown fox jumps over the lazy dog]

result = words
  .uniq                     # remove repeats
  .map { |w| w.upcase }     # transform
  .select { |w| w.length >= 4 }  # filter
  .sort                     # order
  .join(", ")               # terminal: string

puts "pipeline: #{result}"
# -> BROWN, DOG, JUMPS, LAZY, OVER, QUICK

# --- 6. each returns the receiver (a classic gotcha) ------------------------

captured = numbers.each { |_n| }
puts "each returns: #{captured.inspect}"
# -> [1, 2, 3, 4, 5, 6]  (the array itself, not the results!)
# Use map/select when you need the transformed/filtered data.
