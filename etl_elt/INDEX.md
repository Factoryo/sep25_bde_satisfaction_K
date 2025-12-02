# 📋 INDEX DES FICHIERS - MASS SCRAPING

## ✅ Fichiers Créés pour le Mass Scraping

### 📜 Scripts Python

| Fichier | Description | Utilisation |
|---------|-------------|-------------|
| `scripts/test_mass_scraping.py` | **Script de test** - 3 entreprises, 1000 reviews | `python scripts/test_mass_scraping.py` |
| `scripts/mass_scraping.py` | **Script production** - 60+ entreprises, 10000 reviews | `python scripts/mass_scraping.py` |
| `scripts/check_progress.py` | **Monitoring** - Vérifier l'état du scraping | `python scripts/check_progress.py` |
| `scripts/generate_report.py` | **Rapport détaillé** - Analyse complète post-scraping | `python scripts/generate_report.py` |

### 📄 PowerShell

| Fichier | Description | Utilisation |
|---------|-------------|-------------|
| `scraping.ps1` | **Helper script** - Interface simple pour tous les scripts | `.\scraping.ps1 [test\|run\|check\|help]` |

### 📚 Documentation

| Fichier | Contenu |
|---------|---------|
| `QUICKSTART.md` | Guide de démarrage rapide avec visualisations |
| `scripts/SETUP_COMPLETE.md` | Configuration complète et instructions détaillées |
| `scripts/MASS_SCRAPING_README.md` | Documentation technique du mass scraping |
| `INDEX.md` | Ce fichier - Index de tous les fichiers créés |

---

## 🎯 Quelle Documentation Lire ?

### Si vous débutez
→ **`QUICKSTART.md`** - Guide visuel en 3 étapes

### Pour les détails techniques
→ **`scripts/MASS_SCRAPING_README.md`** - Documentation complète

### Après installation
→ **`scripts/SETUP_COMPLETE.md`** - Instructions d'utilisation

### Pour les commandes rapides
→ Utilisez simplement **`.\scraping.ps1 help`**

---

## 🗂️ Structure du Projet

```
etl_elt/
│
├── 📜 scraping.ps1                        # Script PowerShell principal
├── 📄 QUICKSTART.md                       # Guide de démarrage rapide
├── 📄 INDEX.md                            # Ce fichier
│
├── scripts/
│   ├── 🐍 test_mass_scraping.py          # Test (3 entreprises)
│   ├── 🐍 mass_scraping.py               # Production (60+ entreprises)
│   ├── 🐍 check_progress.py              # Monitoring
│   ├── 🐍 generate_report.py             # Rapport détaillé
│   ├── 📄 SETUP_COMPLETE.md              # Guide complet
│   └── 📄 MASS_SCRAPING_README.md        # Doc technique
│
├── scrapers/
│   ├── trustpilot_reviews_scraper.py     # Scraper avec multi-filtres
│   ├── trustpilot_category_scraper.py    # Scraper de catégories
│   └── trustpilot_mass_scraper.py        # Ancien scraper (legacy)
│
├── data/
│   ├── test/                              # Données de test
│   │   ├── apple_com_test.json
│   │   ├── amazon_com_test.json
│   │   └── test_report_*.json
│   │
│   ├── raw/                               # Données production
│   │   ├── apple_com_reviews.json
│   │   ├── amazon_com_reviews.json
│   │   └── ... (60+ fichiers)
│   │
│   └── scraping_report_*.json            # Rapports globaux
│
└── logs/
    └── mass_scraping.log                 # Logs détaillés
```

---

## 🚀 Commandes Essentielles

```powershell
# Navigation
cd etl_elt

# Scripts via PowerShell (RECOMMANDÉ)
.\scraping.ps1 test     # Lancer le test
.\scraping.ps1 run      # Lancer la production
.\scraping.ps1 check    # Vérifier l'état
.\scraping.ps1 help     # Aide

# OU Scripts Python directs
python scripts/test_mass_scraping.py      # Test
python scripts/mass_scraping.py           # Production
python scripts/check_progress.py          # État
python scripts/generate_report.py         # Rapport détaillé

# Monitoring en temps réel
Get-Content logs/mass_scraping.log -Wait -Tail 50
```

---

## 📊 Workflow Complet

```
1. TEST
   .\scraping.ps1 test
   → 3 entreprises, ~30-45 min
   → Vérifier que tout fonctionne

2. VÉRIFICATION
   .\scraping.ps1 check
   → Voir les fichiers générés
   → Valider le format

3. PRODUCTION
   .\scraping.ps1 run
   → 60+ entreprises, ~30-40h
   → Laisser tourner la nuit

4. RAPPORT
   python scripts/generate_report.py
   → Analyse complète des données
   → Statistiques détaillées

5. PROCHAINES ÉTAPES
   → Nettoyage des données
   → Analyse exploratoire (EDA)
   → Machine Learning
   → Dashboard Streamlit
```

---

## 🎓 Fonctionnalités Clés

### ✨ Stratégie Multi-Filtres
Scrape par note d'étoiles (5★→1★) pour contourner la limite de 200 pages.
→ **10,000 reviews** possibles par entreprise au lieu de 2,000

### 🔄 Reprise Automatique
Si le script est interrompu, il reprend où il s'est arrêté.
→ Pas besoin de tout recommencer

### 📊 Monitoring en Temps Réel
Voir la progression pendant le scraping.
→ `check_progress.py` ou logs en direct

### 📝 Rapport Détaillé
Analyse complète après scraping : distributions, top entreprises, catégories.
→ `generate_report.py`

---

## 🗺️ Carte des Dépendances

```
mass_scraping.py
    ↓
    └─→ trustpilot_reviews_scraper.py
            ↓
            └─→ Utilise la stratégie multi-filtres
                    ↓
                    ├─→ Scrape par 5★
                    ├─→ Scrape par 4★
                    ├─→ Scrape par 3★
                    ├─→ Scrape par 2★
                    └─→ Scrape par 1★
                            ↓
                            └─→ Déduplique par review_id
                                    ↓
                                    └─→ Sauvegarde dans data/raw/
```

---

## 📌 Références Rapides

### Logs
- **Emplacement**: `logs/mass_scraping.log`
- **Voir en direct**: `Get-Content logs/mass_scraping.log -Wait -Tail 50`

### Données
- **Test**: `data/test/*.json`
- **Production**: `data/raw/*.json`
- **Rapports**: `data/*_report_*.json`

### Scripts
- **Tout**: `.\scraping.ps1 [action]`
- **Détails**: Voir `scripts/` pour les scripts Python individuels

---

## 💡 Conseils

1. **Toujours tester d'abord** avec `test_mass_scraping.py`
2. **Vérifier les résultats** avec `check_progress.py`
3. **Lancer la production la nuit** (30-40h)
4. **Monitorer avec les logs** en temps réel
5. **Générer le rapport final** avec `generate_report.py`

---

## 🔗 Navigation Rapide

- 🚀 [Démarrage Rapide](QUICKSTART.md)
- 📘 [Setup Complet](scripts/SETUP_COMPLETE.md)
- 📖 [Doc Technique](scripts/MASS_SCRAPING_README.md)
- 🏠 [README Principal](../README.md)

---

**Créé le**: 2025-01-20  
**Dernière mise à jour**: 2025-01-20  
**Version**: 1.0
