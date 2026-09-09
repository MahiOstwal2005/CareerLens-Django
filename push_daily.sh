#!/bin/bash
# A simple script to commit and push daily work

echo "Checking for changes..."
git status -s

if [ -z "$(git status --porcelain)" ]; then 
  echo "No changes to commit."
else
  echo "Adding changes..."
  git add .
  
  # Ask for a commit message, default to current date and time
  DEFAULT_MSG="Daily update: $(date +'%Y-%m-%d %H:%M')"
  read -p "Enter commit message (Press Enter for default: '$DEFAULT_MSG'): " USER_MSG
  
  COMMIT_MSG="${USER_MSG:-$DEFAULT_MSG}"
  
  echo "Committing..."
  git commit -m "$COMMIT_MSG"
  
  echo "Pushing to remote repository..."
  # Assuming main is your default branch
  git push origin main
  
  echo "Done!"
fi
