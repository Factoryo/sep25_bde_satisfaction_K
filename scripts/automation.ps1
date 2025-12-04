# Scripts d'Automatisation - Trustpilot Analytics
# Gestion simplifiée de l'infrastructure et des tâches

# ==============================================
# GESTION DES SERVICES
# ==============================================

function Start-AllServices {
    <#
    .SYNOPSIS
    Démarre tous les services Docker
    #>
    Write-Host "🚀 Démarrage de tous les services..." -ForegroundColor Cyan
    docker-compose up -d
    
    Write-Host "`n⏳ Attente du démarrage des services (30 secondes)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    Show-ServicesStatus
}

function Stop-AllServices {
    <#
    .SYNOPSIS
    Arrête tous les services Docker
    #>
    Write-Host "🛑 Arrêt de tous les services..." -ForegroundColor Cyan
    docker-compose down
    Write-Host "✓ Services arrêtés" -ForegroundColor Green
}

function Restart-AllServices {
    <#
    .SYNOPSIS
    Redémarre tous les services Docker
    #>
    Write-Host "🔄 Redémarrage de tous les services..." -ForegroundColor Cyan
    docker-compose restart
    Start-Sleep -Seconds 20
    Show-ServicesStatus
}

function Show-ServicesStatus {
    <#
    .SYNOPSIS
    Affiche le statut de tous les services
    #>
    Write-Host "`n📊 Statut des services:" -ForegroundColor Cyan
    Write-Host "=" * 70
    
    $services = @(
        @{Name="API Data"; URL="http://localhost:8000/health"; Port=8000},
        @{Name="ML API"; URL="http://localhost:8001/health"; Port=8001},
        @{Name="Dashboard"; URL="http://localhost:8502"; Port=8502},
        @{Name="Airflow"; URL="http://localhost:8080"; Port=8080},
        @{Name="Prometheus"; URL="http://localhost:9090"; Port=9090},
        @{Name="Grafana"; URL="http://localhost:3000"; Port=3000},
        @{Name="Elasticsearch"; URL="http://localhost:9200"; Port=9200},
        @{Name="Kibana"; URL="http://localhost:5601"; Port=5601}
    )
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 2 -ErrorAction Stop
            Write-Host "✓ $($service.Name)" -ForegroundColor Green -NoNewline
            Write-Host " - http://localhost:$($service.Port)" -ForegroundColor Gray
        } catch {
            Write-Host "✗ $($service.Name)" -ForegroundColor Red -NoNewline
            Write-Host " - http://localhost:$($service.Port)" -ForegroundColor Gray
        }
    }
    
    Write-Host "=" * 70
}

# ==============================================
# SCRAPING AUTOMATISÉ
# ==============================================

function Start-DailyScraping {
    <#
    .SYNOPSIS
    Lance le scraping quotidien manuellement
    #>
    Write-Host "📥 Lancement du scraping quotidien..." -ForegroundColor Cyan
    docker-compose exec airflow-scheduler airflow tasks test trustpilot_daily_scraping run_daily_scraping (Get-Date -Format "yyyy-MM-dd")
}

function Show-ScrapingLogs {
    <#
    .SYNOPSIS
    Affiche les logs du dernier scraping
    #>
    if (Test-Path "data/logs/daily_scraping_results.json") {
        $results = Get-Content "data/logs/daily_scraping_results.json" | ConvertFrom-Json
        
        Write-Host "`n📊 Résultats du dernier scraping:" -ForegroundColor Cyan
        Write-Host "Date: $($results.date)"
        Write-Host "Entreprises scrapées: $($results.companies_scraped)"
        Write-Host "Total avis collectés: $($results.total_reviews)"
        Write-Host "Erreurs: $($results.errors.Count)"
        
        if ($results.errors.Count -gt 0) {
            Write-Host "`n⚠️  Erreurs détectées:" -ForegroundColor Yellow
            $results.errors | ForEach-Object { Write-Host "  - $_" }
        }
    } else {
        Write-Host "Aucun résultat de scraping trouvé" -ForegroundColor Yellow
    }
}

# ==============================================
# MONITORING & ALERTS
# ==============================================

function Start-DataDriftMonitoring {
    <#
    .SYNOPSIS
    Lance la détection de data drift
    #>
    Write-Host "🔍 Lancement de la détection de data drift..." -ForegroundColor Cyan
    python scripts/ml/data_drift_monitor.py
}

function Show-DriftReports {
    <#
    .SYNOPSIS
    Affiche les derniers rapports de drift
    #>
    $reports = Get-ChildItem "docs/data_drift_reports" -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
    
    if ($reports.Count -eq 0) {
        Write-Host "Aucun rapport de drift trouvé" -ForegroundColor Yellow
        return
    }
    
    Write-Host "`n📊 Derniers rapports de data drift:" -ForegroundColor Cyan
    foreach ($report in $reports) {
        $content = Get-Content $report.FullName | ConvertFrom-Json
        $driftStatus = if ($content.overall_drift_detected) { "⚠️  DRIFT DÉTECTÉ" } else { "✓ OK" }
        Write-Host "$($report.Name): $driftStatus"
    }
}

function Open-Monitoring {
    <#
    .SYNOPSIS
    Ouvre les dashboards de monitoring dans le navigateur
    #>
    Write-Host "🌐 Ouverture des dashboards..." -ForegroundColor Cyan
    Start-Process "http://localhost:9090"  # Prometheus
    Start-Process "http://localhost:3000"  # Grafana
    Start-Process "http://localhost:8080"  # Airflow
}

# ==============================================
# DÉPLOIEMENT & CI/CD
# ==============================================

function Deploy-ToProduction {
    <#
    .SYNOPSIS
    Déploie vers la production (nécessite GitLab CI)
    #>
    Write-Host "🚀 Déploiement en production..." -ForegroundColor Cyan
    
    # Vérifier que tout est commité
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Host "⚠️  Attention: Changements non committés détectés" -ForegroundColor Yellow
        Write-Host "Voulez-vous continuer? (O/N)" -ForegroundColor Yellow
        $response = Read-Host
        if ($response -ne "O") {
            Write-Host "Déploiement annulé" -ForegroundColor Red
            return
        }
    }
    
    # Push vers main (déclenche le pipeline GitLab)
    Write-Host "Pushing vers main..." -ForegroundColor Cyan
    git push origin main
    
    Write-Host "`n✓ Code pushé! Le pipeline GitLab va démarrer." -ForegroundColor Green
    Write-Host "Suivez le déploiement sur: https://gitlab.com/your-project/-/pipelines" -ForegroundColor Cyan
}

function Test-APIs {
    <#
    .SYNOPSIS
    Lance les tests sur les APIs
    #>
    Write-Host "🧪 Tests des APIs..." -ForegroundColor Cyan
    
    Write-Host "`n1. Test de l'API ML..."
    python api/test_ml_api.py
    
    Write-Host "`n2. Test rapide..."
    python test_quick.py
    
    Write-Host "`n✅ Tests terminés" -ForegroundColor Green
}

# ==============================================
# MAINTENANCE
# ==============================================

function Clean-OldData {
    <#
    .SYNOPSIS
    Nettoie les anciennes données (>30 jours)
    #>
    Write-Host "🧹 Nettoyage des anciennes données..." -ForegroundColor Cyan
    
    # Nettoyer les vieux fichiers JSON
    $oldFiles = Get-ChildItem "data/raw" -Recurse -Filter "*.json" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }
    
    if ($oldFiles.Count -eq 0) {
        Write-Host "Aucun fichier à nettoyer" -ForegroundColor Green
        return
    }
    
    Write-Host "Fichiers à supprimer: $($oldFiles.Count)"
    Write-Host "Voulez-vous continuer? (O/N)" -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "O") {
        $oldFiles | Remove-Item -Force
        Write-Host "✓ $($oldFiles.Count) fichiers supprimés" -ForegroundColor Green
    } else {
        Write-Host "Nettoyage annulé" -ForegroundColor Yellow
    }
}

function Backup-Database {
    <#
    .SYNOPSIS
    Sauvegarde les bases de données
    #>
    $backupDir = "backups/$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    Write-Host "💾 Sauvegarde des bases de données..." -ForegroundColor Cyan
    
    # Backup PostgreSQL
    Write-Host "Backup PostgreSQL..."
    docker-compose exec -T postgres pg_dump -U trustpilot_user trustpilot_db > "$backupDir/postgres.sql"
    
    # Backup Elasticsearch (via snapshots)
    Write-Host "Backup Elasticsearch..."
    # Commande à adapter selon votre configuration
    
    Write-Host "✓ Sauvegarde terminée dans $backupDir" -ForegroundColor Green
}

# ==============================================
# MENU PRINCIPAL
# ==============================================

function Show-Menu {
    Clear-Host
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     TRUSTPILOT ANALYTICS - AUTOMATISATION                ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔧 SERVICES"
    Write-Host "  1. Démarrer tous les services"
    Write-Host "  2. Arrêter tous les services"
    Write-Host "  3. Redémarrer tous les services"
    Write-Host "  4. Afficher le statut"
    Write-Host ""
    Write-Host "📥 SCRAPING"
    Write-Host "  5. Lancer le scraping quotidien"
    Write-Host "  6. Voir les logs de scraping"
    Write-Host ""
    Write-Host "🔍 MONITORING"
    Write-Host "  7. Détecter le data drift"
    Write-Host "  8. Voir les rapports de drift"
    Write-Host "  9. Ouvrir les dashboards"
    Write-Host ""
    Write-Host "🚀 DÉPLOIEMENT"
    Write-Host " 10. Tester les APIs"
    Write-Host " 11. Déployer en production"
    Write-Host ""
    Write-Host "🧹 MAINTENANCE"
    Write-Host " 12. Nettoyer les vieilles données"
    Write-Host " 13. Sauvegarder les bases"
    Write-Host ""
    Write-Host "  0. Quitter"
    Write-Host ""
}

# Boucle principale
while ($true) {
    Show-Menu
    $choice = Read-Host "Choisissez une option"
    
    switch ($choice) {
        "1" { Start-AllServices; Read-Host "Appuyez sur Entrée pour continuer" }
        "2" { Stop-AllServices; Read-Host "Appuyez sur Entrée pour continuer" }
        "3" { Restart-AllServices; Read-Host "Appuyez sur Entrée pour continuer" }
        "4" { Show-ServicesStatus; Read-Host "Appuyez sur Entrée pour continuer" }
        "5" { Start-DailyScraping; Read-Host "Appuyez sur Entrée pour continuer" }
        "6" { Show-ScrapingLogs; Read-Host "Appuyez sur Entrée pour continuer" }
        "7" { Start-DataDriftMonitoring; Read-Host "Appuyez sur Entrée pour continuer" }
        "8" { Show-DriftReports; Read-Host "Appuyez sur Entrée pour continuer" }
        "9" { Open-Monitoring; Read-Host "Appuyez sur Entrée pour continuer" }
        "10" { Test-APIs; Read-Host "Appuyez sur Entrée pour continuer" }
        "11" { Deploy-ToProduction; Read-Host "Appuyez sur Entrée pour continuer" }
        "12" { Clean-OldData; Read-Host "Appuyez sur Entrée pour continuer" }
        "13" { Backup-Database; Read-Host "Appuyez sur Entrée pour continuer" }
        "0" { Write-Host "Au revoir!" -ForegroundColor Cyan; exit }
        default { Write-Host "Option invalide" -ForegroundColor Red; Start-Sleep -Seconds 1 }
    }
}
