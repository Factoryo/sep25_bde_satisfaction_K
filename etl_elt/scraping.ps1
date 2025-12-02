# Script PowerShell pour faciliter le mass scraping
# Usage: .\scraping.ps1 [test|run|check|help]

param(
    [Parameter(Position=0)]
    [ValidateSet('test','run','check','help')]
    [string]$Action = 'help'
)

function Show-Help {
    Write-Host ""
    Write-Host "=============================================================="
    Write-Host "    TRUSTPILOT MASS SCRAPING - Helper Script"
    Write-Host "=============================================================="
    Write-Host ""
    Write-Host "Commandes disponibles:"
    Write-Host ""
    Write-Host "  .\scraping.ps1 test    - Lancer le test (3 entreprises)"
    Write-Host "  .\scraping.ps1 run     - Lancer le scraping complet (60+ entreprises)"
    Write-Host "  .\scraping.ps1 check   - Verifier la progression"
    Write-Host "  .\scraping.ps1 help    - Afficher cette aide"
    Write-Host ""
    Write-Host "=============================================================="
    Write-Host ""
    Write-Host "Documentation complete:" 
    Write-Host "  - scripts/SETUP_COMPLETE.md"
    Write-Host "  - scripts/MASS_SCRAPING_README.md"
    Write-Host ""
}

function Start-Test {
    Write-Host ""
    Write-Host "=============================================================="
    Write-Host "              LANCEMENT DU TEST"
    Write-Host "=============================================================="
    Write-Host ""
    Write-Host "Configuration:"
    Write-Host "  - Entreprises: 3 (Apple, Amazon, Booking)"
    Write-Host "  - Reviews max: ~1000 par entreprise"
    Write-Host "  - Duree estimee: 30-45 minutes"
    Write-Host "  - Sortie: data/test/"
    Write-Host ""

    $confirm = Read-Host "Continuer? (o/n)"
    if ($confirm -ne 'o') {
        Write-Host "[X] Test annule" -ForegroundColor Red
        return
    }

    Write-Host "`nDemarrage du test...`n" -ForegroundColor Green
    
    # Créer les répertoires nécessaires
    New-Item -ItemType Directory -Path "data/test" -Force | Out-Null
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    
    # Lancer le script
    python scripts/test_mass_scraping.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[OK] Test termine avec succes!" -ForegroundColor Green
        Write-Host "Resultats dans: data/test/" -ForegroundColor Cyan
        Write-Host "`nVerifiez les resultats avec: .\scraping.ps1 check`n" -ForegroundColor Yellow
    } else {
        Write-Host "`n[ERREUR] Erreur lors du test" -ForegroundColor Red
        Write-Host "Consultez les logs: logs/mass_scraping.log`n" -ForegroundColor Yellow
    }
}

function Start-Production {
    Write-Host ""
    Write-Host "=============================================================="
    Write-Host "          LANCEMENT DU SCRAPING COMPLET"
    Write-Host "=============================================================="
    Write-Host ""
    Write-Host "ATTENTION: Scraping de longue duree!"
    Write-Host ""
    Write-Host "Configuration:"
    Write-Host "  - Entreprises: 60+"
    Write-Host "  - Reviews max: ~10,000 par entreprise"
    Write-Host "  - Total estime: ~600,000 reviews"
    Write-Host "  - Duree estimee: 30-40 HEURES"
    Write-Host "  - Sortie: data/raw/"
    Write-Host ""
    Write-Host "Recommandations:"
    Write-Host "  - Lancer la nuit ou le weekend"
    Write-Host "  - Garder l'ordinateur allume"
    Write-Host "  - Connexion internet stable"
    Write-Host "  - ~3 GB d'espace disque"
    Write-Host ""

    $confirm = Read-Host "Etes-vous sur de vouloir lancer le scraping complet? (OUI/non)"
    if ($confirm -ne 'OUI') {
        Write-Host "[X] Scraping annule" -ForegroundColor Red
        Write-Host "Tapez 'OUI' en majuscules pour confirmer`n" -ForegroundColor Yellow
        return
    }

    Write-Host "`nDemarrage du scraping massif...`n" -ForegroundColor Green
    Write-Host "Pour interrompre: Ctrl+C (la progression sera sauvegardee)`n" -ForegroundColor Cyan
    
    # Créer les répertoires nécessaires
    New-Item -ItemType Directory -Path "data/raw" -Force | Out-Null
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    
    # Lancer le script
    python scripts/mass_scraping.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[OK] Scraping termine avec succes!" -ForegroundColor Green
        Write-Host "Resultats dans: data/raw/" -ForegroundColor Cyan
        Write-Host "`nGenerez un rapport avec: .\scraping.ps1 check`n" -ForegroundColor Yellow
    } else {
        Write-Host "`n[ATTENTION] Scraping interrompu ou erreur" -ForegroundColor Yellow
        Write-Host "Consultez les logs: logs/mass_scraping.log" -ForegroundColor Yellow
        Write-Host "Vous pouvez relancer, le script reprendra ou il s'est arrete`n" -ForegroundColor Cyan
    }
}

function Check-Progress {
    Write-Host ""
    Write-Host "=============================================================="
    Write-Host "            VERIFICATION DE LA PROGRESSION"
    Write-Host "=============================================================="
    Write-Host ""

    python scripts/check_progress.py
    
    Write-Host ""
    Write-Host "=============================================================="
    Write-Host "Pour voir les logs en temps reel:"
    Write-Host "   Get-Content logs/mass_scraping.log -Wait -Tail 50" -ForegroundColor Cyan
    Write-Host ""
}

# Navigation vers le bon répertoire
if (Test-Path "etl_elt") {
    Set-Location "etl_elt"
}

# Exécution de l'action
switch ($Action) {
    'test' { Start-Test }
    'run' { Start-Production }
    'check' { Check-Progress }
    'help' { Show-Help }
    default { Show-Help }
}
