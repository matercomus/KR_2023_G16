#!/bin/bash

# Create the final_steps directory if it doesn't exist
mkdir -p final_steps

# Loop over the directories
for dir in $(find . -type d -name "*claimed*"); do
	# Get the UID from the parent directory name
	uid=$(basename $dir)

	# Find the last step PNG file in the directory
	last_step_file=$(find $dir -type f -name "*_step_*.png" | sort -V | tail -n 1)

	# Check if the file was found
	if [[ -z "$last_step_file" ]]; then
		echo "Error: No PNG files found in $dir"
	else
		# Get the filename without the directory
		filename=$(basename "$last_step_file")

		# Copy the last step file to the final_steps directory, appending the UID to the filename
		cp "$last_step_file" "final_steps/${filename%.*}_$uid.png"
	fi
done
