# Topic: Classes, modules and mixins - Ruby's answer to multiple inheritance.
#
# Ruby has single inheritance for classes, but a class can mix in any number
# of MODULES. That is how Ruby gets code reuse without the ambiguity of
# multiple inheritance, and it is the single most important design idea in
# the standard library (Enumerable and Comparable are both mixins).
#
# Concepts:
# - Defining classes, attr_reader/writer/accessor, and initialize
# - Instance vs class methods, and @ivar vs @@class-var vs CONSTANT
# - Modules as namespaces AND as mixins (include vs extend vs prepend)
# - Getting Comparable and Enumerable for free by implementing <=> and each
# - The ancestor chain, and how `super` walks it
# - public / private / protected
#
# Run: ruby examples/ruby/oop/classes_modules_and_mixins.rb
#
# NOTE: validated by inspection (no Ruby interpreter on authoring host).

# ---------------------------------------------------------------------------
# 1. A module used purely as a NAMESPACE
# ---------------------------------------------------------------------------
module Library
  # A constant lives on the module: Library::MAX_LOANS
  MAX_LOANS = 3

  # ---------------------------------------------------------------------------
  # 2. A module used as a MIXIN
  # ---------------------------------------------------------------------------
  module Describable
    # Instance methods defined here are added to any class that `include`s it.
    def describe
      "#{self.class.name.split('::').last}: #{title} (#{year})"
    end
  end

  # A module can also hold "class methods" for whoever extends it.
  #
  # CAREFUL: @instances_created here is a CLASS-LEVEL instance variable, and
  # each class gets its OWN. A subclass does not share the parent's counter,
  # so Book.instances_created and Item.instances_created count separately.
  # If you wanted one shared total you would need a @@class_variable (which
  # IS shared down the hierarchy, and is generally discouraged for exactly
  # that reason) or an explicit counter on a single owner.
  module Countable
    def instances_created
      @instances_created ||= 0
    end

    def record_instance
      @instances_created = instances_created + 1
    end
  end

  # ---------------------------------------------------------------------------
  # 3. A class
  # ---------------------------------------------------------------------------
  class Item
    include Describable   # adds INSTANCE methods
    extend Countable      # adds CLASS methods
    include Comparable    # gives <, <=, ==, >, >=, between?, clamp from <=>

    # attr_reader generates a getter; attr_accessor generates both.
    attr_reader :title, :year
    attr_accessor :available

    def initialize(title, year)
      @title = title          # instance variable
      @year = year
      @available = true
      self.class.record_instance
    end

    # Implementing <=> is the ONLY thing Comparable needs. Everything else
    # is derived from it - this is the payoff of the mixin approach.
    def <=>(other)
      year <=> other.year
    end

    def to_s
      "#{title} (#{year})"
    end

    # Everything below this is private until another visibility keyword.
    private

    def internal_id
      "#{title.downcase.gsub(/\s+/, '-')}-#{year}"
    end
  end

  # ---------------------------------------------------------------------------
  # 4. Inheritance plus super
  # ---------------------------------------------------------------------------
  class Book < Item
    attr_reader :author

    def initialize(title, year, author)
      super(title, year)    # call the parent's initialize first
      @author = author
    end

    # Override, but reuse the parent's work via super.
    def describe
      "#{super} by #{author}"
    end
  end

  # ---------------------------------------------------------------------------
  # 5. A collection that becomes Enumerable by defining ONE method
  # ---------------------------------------------------------------------------
  class Shelf
    include Enumerable

    def initialize(items = [])
      @items = items
    end

    def add(item)
      @items << item
      self               # return self so calls can chain
    end

    # Define each, and Enumerable supplies map, select, sort, min, max,
    # group_by, reduce, include?, first, count, each_with_index ... all of it.
    def each(&block)
      @items.each(&block)
      self
    end
  end
end

# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

include_book = Library::Book.new("The Pragmatic Programmer", 1999, "Hunt & Thomas")
older = Library::Item.new("SICP", 1985)
newer = Library::Item.new("Eloquent Ruby", 2011)

puts "-- mixin adds instance methods --"
puts "  #{include_book.describe}"
puts "  #{older.describe}"

puts "-- extend adds class methods --"
puts "  Item.instances_created: #{Library::Item.instances_created}"
puts "  Book.instances_created: #{Library::Book.instances_created}"
puts "  (separate counters: a subclass gets its own class-level ivar)"

puts "-- Comparable, from a single <=> --"
newest = Library::Item.new("Something Recent", 2020)
puts "  older < newer      : #{older < newer}"
puts "  newer.between?     : #{newer.between?(older, newest)}"
puts "  sorted             : #{[newer, older, include_book].sort.map(&:title).inspect}"
puts "  min by year        : #{[newer, older].min.title}"

puts "-- Enumerable, from a single each --"
shelf = Library::Shelf.new
shelf.add(older).add(newer).add(include_book)

puts "  count              : #{shelf.count}"
puts "  titles             : #{shelf.map(&:title).inspect}"
puts "  published after 1990: #{shelf.select { |i| i.year > 1990 }.map(&:year).inspect}"
puts "  oldest             : #{shelf.min_by(&:year).title}"
puts "  grouped by decade  : #{shelf.group_by { |i| (i.year / 10) * 10 }.keys.sort.inspect}"
puts "  any? before 1990   : #{shelf.any? { |i| i.year < 1990 }}"

puts "-- the ancestor chain --"
# Modules appear in the chain, which is exactly how method lookup finds them.
puts "  Book ancestors: #{Library::Book.ancestors.take(6).inspect}"

puts "-- namespacing and constants --"
puts "  Library::MAX_LOANS = #{Library::MAX_LOANS}"

puts "-- visibility --"
puts "  private method via send: #{older.send(:internal_id)}"
begin
  older.internal_id                          # calling it normally raises
rescue NoMethodError => e
  puts "  calling it directly raises: #{e.class}"
end

puts "-- include vs extend, side by side --"
puts "  Item.include?(Library::Describable): #{Library::Item.include?(Library::Describable)}"
puts "  Item.respond_to?(:instances_created): #{Library::Item.respond_to?(:instances_created)}"
puts "  item.respond_to?(:describe):          #{older.respond_to?(:describe)}"

# Expected output:
#   -- mixin adds instance methods --
#     Book: The Pragmatic Programmer (1999) by Hunt & Thomas
#     Item: SICP (1985)
#   -- extend adds class methods --
#     Item.instances_created: 2
#     Book.instances_created: 1
#     (separate counters: a subclass gets its own class-level ivar)
#   -- Comparable, from a single <=> --
#     older < newer      : true
#     sorted             : ["SICP", "The Pragmatic Programmer", "Eloquent Ruby"]
#   -- Enumerable, from a single each --
#     count              : 3
#     titles             : ["SICP", "Eloquent Ruby", "The Pragmatic Programmer"]
#     oldest             : SICP
#   -- the ancestor chain --
#     Book ancestors: [Library::Book, Library::Item, Comparable,
#                      Library::Describable, Object, Kernel]
#   -- visibility --
#     calling it directly raises: NoMethodError
