# Topic: Lazy Enumerable pipelines for bounded work over unbounded input.
# Concepts: Enumerator::Lazy, take as a terminal bound, deferred evaluation.
# Run: ruby examples/ruby/enumerable/lazy_enumeration.rb
# NOTE: validated by inspection (no Ruby toolchain on this host).

examined = 0

numbers = (1..).lazy.map do |number|
  examined += 1
  number * number
end

first_even_squares = numbers.select(&:even?).take(4).force

raise "wrong values" unless first_even_squares == [4, 16, 36, 64]
raise "pipeline was eager" unless examined == 8

puts "values: #{first_even_squares.join(', ')}"
puts "source values examined: #{examined}"

# Without `.lazy`, map attempts to consume the endless range immediately.
# Without a terminal operation such as `take(...).force`, no work happens.
