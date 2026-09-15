# Topic: Symbol #to_proc — calling a named method on each element.
#
# Concepts:
#   - Passing a block to array methods (map, select, sort_by)
#   - Converting a Symbol to a proc with .to_proc
#   - Passing the symbol directly (Array methods accept it implicitly)
#   - Built-in method symbols as common shorthand:
#     :upcase, :downcase, :to_s, :length, :strip, :round
#
# Example output:
#   names: ["ada", "grace", "linus"]
#   mapped:  ["ADA", "GRACE", "LINUS"]
#   mapped via &: ["ADA", "GRACE", "LINUS"]
#   longest: hello (length 5)
#   cleaned: ["Ada", "Grace"]

names = ["ada", "grace", "linus"]
puts "names: #{names.inspect}"

# The explicit-block way:
upcased = names.map { |n| n.upcase }
puts "mapped:  #{upcased.inspect}"

# The same thing via Symbol#to_proc: :upcase.to_proc is a proc that
# calls .upcase on whatever it is called with.
via_to_proc = names.map(&:upcase)  # & turns the symbol into a block
puts "mapped via &: #{via_to_proc.inspect}"

# These two are equivalent:
explicit = [3, 1, 4, 1, 5].sort_by { |n| n.to_s.length }
shorthand = [3, 1, 4, 1, 5].sort_by(&:to_s.length)
raise "mismatch!" unless explicit == shorthand

# :length works on both strings and arrays:
words = ["hi", "hello", "hey"]
longest = words.max_by(&:length)
puts "longest: #{longest} (length #{longest.length})"

# Chaining several symbol procs:
raw = ["  Ada  ", " grace "]
cleaned = raw.map(&:strip).map(&:capitalize)
puts "cleaned: #{cleaned.inspect}"
