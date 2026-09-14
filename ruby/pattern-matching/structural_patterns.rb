# Ruby pattern matching destructures arrays and hashes while checking their shape.

def describe_event(event)
  case event
  in { type: "login", user: { id:, name: } }
    "#{name} (##{id}) logged in"
  in { type: "purchase", total: 100.., items: [first, *rest] }
    "large purchase: #{first[:name]} plus #{rest.length} more item(s)"
  in { type: "purchase", total:, items: [] }
    "empty purchase worth #{total}"
  in { type: "error", code: 400..499 => code, message: }
    "client error #{code}: #{message}"
  else
    "unknown event"
  end
end

events = [
  { type: "login", user: { id: 7, name: "Mina" } },
  {
    type: "purchase",
    total: 125,
    items: [{ name: "Keyboard" }, { name: "Mouse" }]
  },
  { type: "error", code: 404, message: "not found" },
  { type: "logout" }
]

events.each { |event| puts describe_event(event) }

# `=> variable` captures the value that matched a sub-pattern.
coordinates = [3, 3]
case coordinates
in [Integer => x, Integer => y] if x == y
  puts "point lies on x = y at #{x}"
else
  puts "ordinary point"
end

# The pin operator (^) compares against an existing variable instead of binding.
expected_role = "admin"
user = { name: "Arun", role: "admin" }

case user
in { name:, role: ^expected_role }
  puts "authorized administrator: #{name}"
else
  puts "not an administrator"
end
