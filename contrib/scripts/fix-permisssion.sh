!/bin/bash
Directories[0]="."

# Setup find correctly.
export IFS=$'\n'

# Loop through our array.
for x in ${Directories[@]}
	do
		# Find all directories & subdirectories
		for i in $(find $x -type d)
			do
				# Fix Permissions
				chmod -c 775 $i
				chown -c www-data:www-data $i
			done

		# Find all Files
		for i in $(find $x -type f)
			do
				# Fix Permissions
				chmod -c 664 $i
				chown -c www-data:www-data $i
			done
	done
