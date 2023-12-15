# Get Django settings using a management command
PROJECT_DIR='https://ci-chathub-bucket.s3.amazonaws.com'

# Define an array of app names
APPS=("group_chat" "messaging" "user_profile")

# Minify CSS and JS files for each app
for app_name in "${APPS[@]}"; do
  # Minify CSS files for the current app
  find "$PROJECT_DIR/static/$app_name/css/" -type f -name '*.css' -print0 | while IFS= read -r -d $'\0' css_file; do
    # Minify CSS and overwrite the original file
    cleancss "$css_file" -o "$css_file"
  done

  # Minify JS files for the current app
  find "$PROJECT_DIR/static/$app_name/js/" -type f -name '*.js' -print0 | while IFS= read -r -d $'\0' js_file; do
    # Minify JS and overwrite the original file
    uglifyjs "$js_file" -o "$js_file"
  done
done

# Minify CSS and JS files for the root level static folder
find "$PROJECT_DIR/static/" -type f \( -name '*.css' -o -name '*.js' \) -print0 | while IFS= read -r -d $'\0' file; do
  # Minify CSS or JS based on file extension and overwrite the original file
  if [[ "$file" == *.css ]]; then
    cleancss "$file" -o "$file"
  elif [[ "$file" == *.js ]]; then
    uglifyjs "$file" -o "$file"
  fi
done


