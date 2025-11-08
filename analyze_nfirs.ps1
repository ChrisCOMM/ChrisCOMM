# PowerShell Script to Analyze NFIRS Data on Windows
# Save as: analyze_nfirs.ps1
# Run: .\analyze_nfirs.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "NFIRS Solar Panel & Battery Fire Analysis" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$zipFile = "C:\Users\EU01242390\Downloads\nfirs_all_incident_pdr_2024.zip"

# Check if file exists
if (-not (Test-Path $zipFile)) {
    Write-Host "Error: File not found: $zipFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please update the zipFile variable in this script."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "ZIP File: $zipFile" -ForegroundColor Green
Write-Host "Size: $((Get-Item $zipFile).Length / 1MB) MB" -ForegroundColor Green
Write-Host ""

# Step 1: Extract
Write-Host "Step 1: Extracting NFIRS data..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
}

Expand-Archive -Path $zipFile -DestinationPath "data" -Force
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 2: List files
Write-Host "Step 2: Extracted files:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Get-ChildItem -Path "data\*.csv" | Format-Table Name, @{Name="Size (MB)";Expression={"{0:N2}" -f ($_.Length / 1MB)}}
Write-Host ""

# Step 3: Install dependencies
Write-Host "Step 3: Checking Python dependencies..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
pip install -q pandas pyyaml click numpy
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 4: Check data statistics
Write-Host "Step 4: Data Statistics..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

$basicFile = Get-ChildItem -Path "data" -Filter "*basic*.csv" | Select-Object -First 1

if ($basicFile) {
    Write-Host "Found basic module: $($basicFile.Name)" -ForegroundColor Green
    python src/main.py stats --input "data\$($basicFile.Name)"
} else {
    Write-Host "Warning: Basic incident file not found" -ForegroundColor Red
    Write-Host "Available files:"
    Get-ChildItem -Path "data\*.csv" | ForEach-Object { Write-Host "  - $($_.Name)" }
}
Write-Host ""

# Step 5: Run analysis
Write-Host "Step 5: Running Solar Panel & Battery Fire Analysis..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

python src/main.py analyze --type all --year 2024 --format all

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Analysis Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Find latest report
$latestReport = Get-ChildItem -Path "reports" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($latestReport) {
    Write-Host "Reports saved to: reports\$($latestReport.Name)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Files:" -ForegroundColor Yellow
    Get-ChildItem -Path "reports\$($latestReport.Name)" | ForEach-Object {
        Write-Host "  $($_.Name)" -ForegroundColor White
    }
    Write-Host ""

    # Ask to open HTML report
    $htmlReport = Get-ChildItem -Path "reports\$($latestReport.Name)\report.html"
    if ($htmlReport) {
        $response = Read-Host "Open HTML report in browser? (Y/N)"
        if ($response -eq "Y" -or $response -eq "y") {
            Start-Process $htmlReport.FullName
        }
    }
}

Write-Host ""
Read-Host "Press Enter to exit"
