#!/bin/bash
# Run syntax: ./parser.sh <-i|-e> "search_string" <dir/path>
while getopts ":e:i:" opt; do
  case $opt in
    e) exclude_string=$OPTARG ;;
    i) include_string=$OPTARG ;;
    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

shift $((OPTIND - 1))

# Check if a directory argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 [-e exclude_string] [-i include_string] directory"
  exit 1
fi

directory="$1"

# Check if the directory exists
if [ ! -d "$directory" ]; then
  echo "Directory does not exist."
  exit 1
fi

# Iterate over all files in the directory
for file in "$directory"/*.grab; do
  # Check if the file exists and is a regular file (i.e. not a directory or symlink)
  if [ -f "$file" ]; then
    # Check if the file contains the include string if provided
    if [ -n "$include_string" ]; then
      if grep -q "$include_string" "$file"; then
        echo "$(basename "$file") contains $include_string"
      fi
    fi

    # Check if the file contains the exclude string if provided
    if [ -n "$exclude_string" ]; then
      if ! grep -q "$exclude_string" "$file"; then
        echo -e "$(basename "$file") does not contain $exclude_string"
      fi
    fi
  fi
done
