# ✅ MASS SCRAPING - Configuration Terminée

## 🎯 Objectif
Scraper **60+ entreprises** avec **10,000+ reviews** chacune en utilisant la **stratégie multi-filtres**.

---

## 📁 Fichiers Créés

### Scripts Principaux
1. **`test_mass_scraping.py`** - Test sur 3 entreprises (~1000 reviews chacune)
2. **`mass_scraping.py`** - Production sur 60+ entreprises (~10000 reviews chacune)  
3. **`check_progress.py`** - Vérification de l'état du scraping
4. **`MASS_SCRAPING_README.md`** - Documentation complète

---

## 🚀 Quick Start

### Étape 1: Test (Recommandé d'abord!)
```powershell
cd etl_elt
python scripts/test_mass_scraping.py
```

**Durée estimée**: ~30-45 minutes  
**Résultat attendu**: 3 fichiers JSON dans `data/test/` avec ~3000 reviews au total

---

### Étape 2: Vérifier les résultats du test
```powershell
python scripts/check_progress.py
```

Ceci affichera :
- ✅ Nombre de fichiers créés
- 📊 Statistiques par entreprise
- 📝 Total de reviews scrapées

---

### Étape 3: Lancer la production (si test OK)
```powershell
python scripts/mass_scraping.py
```

**Durée estimée**: ~30-40 heures  
**Résultat attendu**: 60 fichiers JSON dans `data/raw/` avec ~600,000 reviews au total

⚠️ **Important**: Laisser tourner pendant la nuit ou le weekend

---

### Étape 4: Monitorer la progression
```powershell
# Dans un autre terminal PowerShell
cd etl_elt

# Voir les logs en temps réel
Get-Content logs/mass_scraping.log -Wait -Tail 50

# OU vérifier l'état actuel
python scripts/check_progress.py
```

---

## 🔄 Stratégie Multi-Filtres

### Pourquoi c'est efficace ?
Trustpilot limite la pagination standard à ~200 pages (2000 reviews).

Notre solution :
```
5★ reviews → jusqu'à 2000 reviews
4★ reviews → jusqu'à 2000 reviews
3★ reviews → jusqu'à 2000 reviews
2★ reviews → jusqu'à 2000 reviews
1★ reviews → jusqu'à 2000 reviews
────────────────────────────────
TOTAL      → jusqu'à 10,000 reviews
```

Les reviews sont **automatiquement dédupliquées** par ID unique.

---

## 📊 Liste des 60+ Entreprises

### E-commerce (8)
amazon.com, amazon.co.uk, ebay.com, aliexpress.com, wish.com, etsy.com, walmart.com, target.com

### Tech (6)
apple.com, microsoft.com, google.com, samsung.com, dell.com, hp.com

### Services & Apps (8)
facebook.com, instagram.com, twitter.com, tiktok.com, netflix.com, spotify.com, zoom.us, paypal.com

### Travel & Transport (7)
booking.com, airbnb.com, expedia.com, tripadvisor.com, uber.com, lyft.com, ryanair.com

### Fashion & Lifestyle (5)
asos.com, zara.com, hm.com, nike.com, adidas.com

### Food Delivery (3)
ubereats.com, deliveroo.com, doordash.com

### Telecom (3)
verizon.com, att.com, t-mobile.com

### Finance (3)
revolut.com, n26.com, coinbase.com

### France Spécifique (9)
showroomprive.com, vinted.fr, leboncoin.fr, cdiscount.com, fnac.com, sncf.com, orange.fr, freemobile.fr, bouyguestelecom.fr

**TOTAL: 60 entreprises**

---

## 📋 Données Collectées

### Par Review (30+ champs)
- **Identifiants**: review_id, review_link
- **Reviewer**: reviewer_name, reviewer_review_count, reviewer_location
- **Dates**: review_date (absolute), review_date_relative
- **Scores**: stars (1-5), rating_score (0-10)
- **Contenu**: review_title, review_text
- **Entreprise**: company_name, company_reply, company_reply_date
- **Métadonnées**: verified_purchase, review_language, helpful_count

### Par Entreprise
- company_name, trust_score, total_reviews
- categories, website, contact_info

---

## 🛠️ Commandes Utiles

### Vérifier l'espace disque
```powershell
# Voir l'espace disponible
Get-PSDrive C | Select-Object Used,Free

# Voir la taille du dossier data
(Get-ChildItem -Path data -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB
```

### Compter les reviews scrapées
```powershell
# Nombre de fichiers JSON
(Get-ChildItem data/raw/*.json).Count

# Voir la progression
python scripts/check_progress.py
```

### Interrompre le scraping
```
Ctrl+C dans le terminal où tourne le script
```
Le script sauvegarde la progression, vous pouvez relancer plus tard.

---

## ⚠️ Troubleshooting

### "Module not found: scrapers"
```powershell
cd etl_elt  # Assurez-vous d'être dans le bon répertoire
```

### "Permission denied" sur logs
```powershell
New-Item -ItemType Directory -Path logs -Force
```

### Le script est trop lent
- C'est normal ! Scraper 10000 reviews prend du temps
- Le délai de 2s entre pages est nécessaire pour éviter le rate limiting
- Pour 60 entreprises × 10000 reviews = 30-40 heures

### Reviews < 10000 pour une entreprise
Certaines entreprises n'ont pas 10000 reviews disponibles, c'est normal.

---

## 📈 Progression Attendue

| Temps | Entreprises | Reviews Estimées |
|-------|-------------|------------------|
| 1h    | ~2          | ~20,000          |
| 6h    | ~10         | ~100,000         |
| 12h   | ~20         | ~200,000         |
| 24h   | ~40         | ~400,000         |
| 36h   | ~60         | ~600,000         |

---

## ✨ Prochaines Étapes (Après Scraping)

1. **Nettoyage des données**
   - Supprimer les doublons
   - Normaliser les dates
   - Détecter la langue

2. **Analyse exploratoire (EDA)**
   - Distribution des notes
   - Tendances temporelles
   - Analyse de sentiment

3. **Modèle ML**
   - Prédiction de satisfaction
   - Classification de sentiment
   - Détection de thèmes

4. **Dashboard interactif**
   - Visualisation Streamlit
   - Métriques temps réel
   - Comparaison entre entreprises

5. **Orchestration Airflow**
   - Scraping automatique quotidien
   - Pipeline ETL complet

---

## 📞 Support

Si vous rencontrez un problème :
1. Vérifier les logs: `logs/mass_scraping.log`
2. Lancer `python scripts/check_progress.py` pour diagnostiquer
3. Consulter `MASS_SCRAPING_README.md` pour la doc détaillée

---

**✅ Configuration terminée ! Vous êtes prêt à lancer le scraping massif.**

Commencez par le test :
```powershell
cd etl_elt
python scripts/test_mass_scraping.py
```
