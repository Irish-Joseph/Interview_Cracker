# Topic: Forwarding positional, keyword, and block arguments in Ruby.
# Concepts: *args vs **kwargs, &block, and the Ruby 3 keyword separation.
# Run: ruby keyword_argument_forwarding.rb
# NOTE: validated by inspection (no Ruby toolchain on this host).
# Expected output: deploy api x3 [dry-run]

def announce(service, times: 1, dry_run: false)
  suffix = dry_run ? " [dry-run]" : ""
  message = "deploy #{service} x#{times}#{suffix}"
  block_given? ? yield(message) : message
end

def logged_call(*args, **kwargs, &block)
  # Ruby 3 keeps positional hashes separate from keyword arguments. Forward
  # both explicitly or a callee with keywords may receive the wrong shape.
  result = announce(*args, **kwargs, &block)
  raise "callee returned nothing" if result.nil?

  result
end

output = logged_call("api", times: 3, dry_run: true) do |message|
  message
end

raise "unexpected forwarding result" unless output == "deploy api x3 [dry-run]"
puts output

# Ruby 2.7+ also supports `def wrapper(...); target(...); end` when the
# wrapper forwards everything unchanged and does not need to inspect it.
