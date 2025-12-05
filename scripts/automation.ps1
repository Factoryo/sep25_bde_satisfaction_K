# Script Automatisation Trustpilot Analytics

function Start-AllServices {
    Write-Host "Demarrage des services..." -ForegroundColor Cyan
    docker-compose up -d
    Start-Sleep -Seconds 30
    Show-ServicesStatus
}

function Stop-AllServices {
    Write-Host "Arret des services..." -ForegroundColor Cyan
    docker-compose down
    Write-Host "Services arretes" -ForegroundColor Green
}

function Show-ServicesStatus {
    Write-Host "`nSTATUS DES SERVICES" -ForegroundColor Cyan
    
    $services = @(
        @{Name="API"; URL="http://localhost:8000/health"},
        @{Name="ML API"; URL="http://localhost:8001/health"},
        @{Name="Dashboard"; URL="http://localhost:8502"},
        @{Name="Airflow"; URL="http://localhost:8080"}
    )
    
    foreach ($service in $services) {
        try {
            Invoke-WebRequest -Uri $service.URL -TimeoutSec 2 -ErrorAction Stop | Out-Null
            Write-Host "[OK] $($service.Name)" -ForegroundColor Green
        } catch {
            Write-Host "[KO] $($service.Name)" -ForegroundColor Red
        }
    }
}

function Start-DailyScraping {
    Write-Host "Lancement du scraping..." -ForegroundColor Cyan
    docker-compose exec airflow-scheduler airflow dags trigger trustpilot_daily_scraping
}

function Show-Menu {
    Clear-Host
    Write-Host "=== TRUSTPILOT ANALYTICS ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Demarrer les services"
    Write-Host "2. Arreter les services"
    Write-Host "3. Status des services"
    Write-Host "4. Lancer scraping"
    Write-Host "0. Quitter"
    Write-Host ""
}

while ($true) {
    Show-Menu
    $choice = Read-Host "Option"
    
    switch ($choice) {
        "1" { Start-AllServices; Read-Host "Appuyez sur Entree" }
        "2" { Stop-AllServices; Read-Host "Appuyez sur Entree" }
        "3" { Show-ServicesStatus; Read-Host "Appuyez sur Entree" }
        "4" { Start-DailyScraping; Read-Host "Appuyez sur Entree" }
        "0" { exit }
        default { Write-Host "Option invalide" -ForegroundColor Red }
    }
}
