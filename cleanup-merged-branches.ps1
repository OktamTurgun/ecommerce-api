# cleanup-merged-branches.ps1
# Main branchga merge bo'lgan local va remote branchlarni avtomatik o'chirish

Write-Host "➡️  Local branchlarni yangilash..."
git fetch --all --prune

# Variant tanlash
Write-Host "`nQaysi tozalash turini xohlaysiz?"
Write-Host "1 - Faqat LOCAL branchlarni o'chirish"
Write-Host "2 - Faqat REMOTE branchlarni o'chirish"
Write-Host "3 - Ikkalasini ham (default)"
$choice = Read-Host "Tanlang (1/2/3)"

if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "3" }

# Local branchlarni o‘chirish
if ($choice -eq "1" -or $choice -eq "3") {
    Write-Host "➡️  Merge qilingan local branchlarni topish..."
    $mergedBranches = git branch --merged main | ForEach-Object { $_.Trim() } | Where-Object { ($_ -ne "main") -and ($_ -ne "* main") }

    foreach ($branch in $mergedBranches) {
        Write-Host "   ❌ Local branch o'chirilyapti: $branch"
        git branch -d $branch
    }
}

# Remote branchlarni o‘chirish
if ($choice -eq "2" -or $choice -eq "3") {
    Write-Host "➡️  Merge qilingan remote branchlarni topish..."
    $remoteMerged = git branch -r --merged origin/main | ForEach-Object { $_.Trim() } | Where-Object { ($_ -notmatch "origin/main") -and ($_ -notmatch "HEAD") }

    foreach ($branch in $remoteMerged) {
        $cleanName = $branch -replace "origin/", ""
        Write-Host "   ❌ Remote branch o'chirilyapti: $cleanName"
        git push origin --delete $cleanName
    }
}

Write-Host "✅ Tozalash tugadi! Endi faqat main va merge qilinmagan branchlar qoldi."
