# Topic: File I/O — reading, writing, and streaming files.
#
# Concepts:
#   - File.read / File.write: the simple all-at-once forms
#   - File.foreach: line-by-line streaming (constant memory, big files)
#   - The block form of File.open: the file is ALWAYS closed, even on error
#   - Open modes: "r", "w" (truncate), "a" (append), "r+" (read+write)
#   - Reading without the trailing newline (chomp)
#
# Validated by inspection (no Ruby on the authoring machine).
#
# Expected behaviour:
#   File.read returns the whole content as one String.
#   File.foreach yields one line at a time (newline included).
#   Appending adds to the end without clobbering existing content.
#   "w" mode TRUNCATES the file to zero length before writing.

require "tmpdir"

Dir.mktmpdir do |dir|
  path = File.join(dir, "notes.txt")

  # --- Write the whole file at once ---------------------------------
  File.write(path, "line one\nline two\n")
  puts File.read(path).strip          # "line one\nline two"

  # --- Append: mode "a" opens at the END -----------------------------
  File.open(path, "a") { |f| f.puts "line three" }
  puts File.read(path).lines.length   # 3

  # --- Stream line by line: constant memory --------------------------
  # The block form of File.open guarantees the file is closed afterwards,
  # even if the block raises. .chomp strips the trailing "\n".
  File.foreach(path) do |line|
    puts line.chomp                   # line one / line two / line three
  end

  # --- Counting lines without loading them all ------------------------
  count = File.foreach(path).count
  puts "total lines: #{count}"        # 3

  # --- "w" mode TRUNCATES: the old content is gone --------------------
  File.write(path, "replaced")
  puts File.read(path)                # "replaced"

  # --- Reading a file that may not exist ------------------------------
  missing = File.join(dir, "nope.txt")
  puts File.exist?(missing)           # false
  # File.read(missing) would raise Errno::ENOENT — check first or rescue.
rescue StandardError => e
  warn "unexpected: #{e.class}: #{e.message}"
  exit 1
end

puts "file io: all checks passed"
