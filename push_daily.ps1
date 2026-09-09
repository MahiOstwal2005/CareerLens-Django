Write-Host "Checking for changes..."
$status = git status --porcelain

if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "No changes to commit."
} else {
    Write-Host "Adding changes..."
    git add .
    
    $defaultMsg = "Daily update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    $userMsg = Read-Host "Enter commit message (Press Enter for default: '$defaultMsg')"
    
    if ([string]::IsNullOrWhiteSpace($userMsg)) {
        $commitMsg = $defaultMsg
    } else {
        $commitMsg = $userMsg
    }
    
    Write-Host "Committing..."
    git commit -m "$commitMsg"
    
    Write-Host "Pushing to remote repository..."
    git push origin main
    
    Write-Host "Done!"
}
