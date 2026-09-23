# Topic: lambda vs proc - three behaviours that differ, and when it matters
#
# A lambda and a proc are both blocks you can hand around. In most code
# either works; in three situations they behave differently, and those are
# the situations that bite:
#
#   1. arity   - a proc ignores extra arguments (and fills missing ones
#                with nil); a lambda raises ArgumentError on a count mismatch
#   2. return  - `return` inside a proc returns from the ENCLOSING METHOD
#                (skipping the rest of it); inside a lambda it returns only
#                from the lambda
#   3. raise   - an exception in a proc unwinds PAST the method that created
#                it; an exception in a lambda is catchable at its own call
#                site, like any normal method
#
# Rules of thumb:
#   - writing a callback you will call later like a method? use a lambda
#   - passing a block to a library that says &block / yields? a proc is fine
#   - `->(x) { }` is lambda syntax; `proc { }` and bare `{ }` are proc syntax
#
# Run: ruby lambda_vs_proc.rb
# NOTE: validated by inspection (no Ruby toolchain on this host); the expected
# output below follows directly from Ruby's documented block semantics.

puts "== 1. arity =="
loose = proc { |a, b| [a, b] }
strict = ->(a, b) { [a, b] }

p loose.call(1)          # [1, nil]      <- missing arg becomes nil
p loose.call(1, 2, 3)    # [1, 2]        <- extra arg silently dropped
begin
  strict.call(1)
rescue ArgumentError => e
  puts "lambda: #{e.message}"
end
begin
  strict.call(1, 2, 3)
rescue ArgumentError => e
  puts "lambda: #{e.message}"
end

puts
puts "== 2. return: the proc escapes its method =="
def demo_proc
  block = proc { return "from the proc" }
  block.call
  "the line after block.call - NEVER REACHED"
end
p demo_proc

def demo_lambda
  block = -> { return "from the lambda" }
  block.call
  "the line after block.call - REACHED"
end
p demo_lambda

puts
puts "== 3. raise: where the exception can be caught =="
def proc_raises
  block = proc { raise "boom from proc" }
  begin
    block.call
  rescue RuntimeError
    "caught at the call site - but this is NEVER reached"
  end
end
begin
  proc_raises
rescue RuntimeError
  puts "proc: caught OUTSIDE the defining method"
end

def lambda_raises
  block = -> { raise "boom from lambda" }
  begin
    block.call
  rescue RuntimeError
    "caught at the call site - normal method-like behaviour"
  end
end
puts "lambda: #{lambda_raises}"

=begin
Expected output (Ruby 3.x):

== 1. arity ==
[1, nil]
[1, 2]
lambda: wrong number of arguments (given 1, expected 2)
lambda: wrong number of arguments (given 3, expected 2)

== 2. return: the proc escapes its method ==
"from the proc"
"the line after block.call - REACHED"

== 3. raise: where the exception can be caught ==
proc: caught OUTSIDE the defining method
lambda: caught at the call site - normal method-like behaviour
=end
