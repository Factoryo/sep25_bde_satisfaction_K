# 🎯 GUIDE DE DÉMARRAGE RAPIDE

## ⚡ En 3 Étapes

```
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 1: TEST (30-45 minutes)                              │
│  ─────────────────────────────────────────────────────────  │
│  cd etl_elt                                                 │
│  .\scraping.ps1 test                                        │
│                                                             │
│  ✓ 3 entreprises                                            │
│  ✓ ~1000 reviews chacune                                    │
│  ✓ Vérifier que tout fonctionne                             │
└─────────────────────────────────────────────────────────────┘

        ↓

┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 2: VÉRIFICATION                                      │
│  ─────────────────────────────────────────────────────────  │
│  .\scraping.ps1 check                                       │
│                                                             │
│  ✓ Voir les fichiers générés                                │
│  ✓ Vérifier les statistiques                                │
│  ✓ S'assurer que le format est correct                      │
└─────────────────────────────────────────────────────────────┘

        ↓

┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 3: PRODUCTION (30-40 heures)                         │
│  ─────────────────────────────────────────────────────────  │
│  .\scraping.ps1 run                                         │
│                                                             │
│  ✓ 60+ entreprises                                          │
│  ✓ ~10,000 reviews chacune                                  │
│  ✓ Lancer la nuit/weekend                                   │
│  ✓ ~600,000 reviews au total                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Structure des Fichiers Générés

```
etl_elt/
├── data/
│   ├── test/                              # Résultats de test
│   │   ├── apple_com_test.json           # ~1000 reviews Apple
│   │   ├── amazon_com_test.json          # ~1000 reviews Amazon
│   │   ├── booking_com_test.json         # ~1000 reviews Booking
│   │   └── test_report_*.json            # Rapport du test
│   │
│   └── raw/                               # Résultats production
│       ├── apple_com_reviews.json        # ~10000 reviews Apple
│       ├── amazon_com_reviews.json       # ~10000 reviews Amazon
│       ├── ... (60+ fichiers)            # ~10000 reviews chacun
│       └── scraping_report_*.json        # Rapport global
│
└── logs/
    └── mass_scraping.log                 # Logs détaillés
```

---

## 📊 Format des Données (JSON)

```json
{
  "company_info": {
    "company_name": "Apple",
    "trust_score": 4.5,
    "total_reviews": 125847,
    "categories": ["Electronics & Technology"],
    "website": "https://www.apple.com"
  },
  "reviews": [
    {
      "review_id": "abc123xyz",
      "review_link": "https://...",
      "company_name": "Apple",
      "reviewer_name": "John D.",
      "reviewer_review_count": 15,
      "review_date": "2024-01-15",
      "review_date_relative": "Il y a 2 mois",
      "stars": 5,
      "rating_score": 10,
      "review_title": "Excellent produit",
      "review_text": "Très satisfait de mon achat...",
      "company_replied": true,
      "company_reply_text": "Merci pour votre retour...",
      "company_reply_date": "2024-01-16"
    }
    // ... 9,999 autres reviews
  ],
  "scraped_at": "2025-01-20T14:30:00",
  "total_reviews": 10000
}
```

---

## 🔍 Monitoring en Temps Réel

### Voir les logs pendant le scraping
```powershell
# Ouvrir un nouveau terminal PowerShell
cd etl_elt
Get-Content logs/mass_scraping.log -Wait -Tail 50
```

### Compter les fichiers générés
```powershell
# Nombre de fichiers en production
(Get-ChildItem data/raw/*.json).Count

# Nombre de fichiers de test
(Get-ChildItem data/test/*.json).Count
```

### Voir l'espace disque utilisé
```powershell
# Taille du dossier data
(Get-ChildItem -Path data -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB
```

---

## ⏱️ Timeline Estimée

```
Production (60+ entreprises × 10,000 reviews):

Heure 0  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0/60   (~0 reviews)
Heure 1  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░   2/60   (~20k reviews)
Heure 6  ████████████░░░░░░░░░░░░░░░░░░░░  10/60   (~100k reviews)
Heure 12 ████████████████████░░░░░░░░░░░░  20/60   (~200k reviews)
Heure 24 ████████████████████████████████░  40/60   (~400k reviews)
Heure 36 ████████████████████████████████  60/60   (~600k reviews) ✓
```

---

## 🔄 Stratégie Multi-Filtres

### Pourquoi ?
Trustpilot limite à **~200 pages** (2000 reviews) en navigation standard.

### Solution
Scraper par note d'étoiles séparément :

```
┌─────────────────────────────────────────┐
│  5★ → Scrape jusqu'à 200 pages          │
│  4★ → Scrape jusqu'à 200 pages          │
│  3★ → Scrape jusqu'à 200 pages          │
│  2★ → Scrape jusqu'à 200 pages          │
│  1★ → Scrape jusqu'à 200 pages          │
├─────────────────────────────────────────┤
│  TOTAL: ~1000 pages = 10,000 reviews    │
└─────────────────────────────────────────┘
```

Les doublons sont automatiquement supprimés par ID unique.

---

## 🛠️ Commandes Essentielles

```powershell
# Lancer le test
.\scraping.ps1 test

# Vérifier l'état
.\scraping.ps1 check

# Lancer la production
.\scraping.ps1 run

# Voir l'aide
.\scraping.ps1 help

# Interrompre (Ctrl+C, puis relancer)
# Le script reprendra où il s'est arrêté
```

---

## ✅ Checklist Avant Production

- [ ] Test exécuté avec succès (3 entreprises)
- [ ] Fichiers JSON vérifiés dans `data/test/`
- [ ] Format des données conforme (company_info + reviews)
- [ ] ~3000 reviews obtenues au test (3 × 1000)
- [ ] Espace disque ≥ 3 GB disponible
- [ ] Connexion internet stable
- [ ] Ordinateur qui restera allumé 30-40h

---

## 📌 Notes Importantes

### Rate Limiting
- **2 secondes** entre chaque page
- **5-10 secondes** entre chaque entreprise
- Respecte les bonnes pratiques de scraping

### Reprise Automatique
Si le script est interrompu (Ctrl+C, coupure réseau) :
```powershell
# Simplement relancer, il reprendra où il s'est arrêté
.\scraping.ps1 run
```

### Stockage
- **Test**: ~50 MB (3 entreprises)
- **Production**: ~2-3 GB (60 entreprises)
- Format JSON non compressé

---

## 🎓 Prochaines Étapes Après Scraping

```
1. NETTOYAGE     → Normaliser dates, supprimer doublons
2. EDA           → Analyser distributions, tendances
3. ML            → Entraîner modèles de sentiment
4. DASHBOARD     → Visualiser dans Streamlit
5. AIRFLOW       → Automatiser le pipeline
```

---

## 📞 Aide & Support

| Problème | Solution |
|----------|----------|
| Module not found | `cd etl_elt` puis relancer |
| Permission denied | `New-Item -Path logs -ItemType Directory -Force` |
| Reviews < 10000 | Normal si l'entreprise n'a pas assez d'avis |
| Script lent | C'est normal, respect du rate limiting |

**Logs détaillés**: `logs/mass_scraping.log`

---

## 🎉 Bon Scraping !

Commencez maintenant :
```powershell
cd etl_elt
.\scraping.ps1 test
```
