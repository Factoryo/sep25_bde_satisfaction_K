# 🚀 Scraping Massif Trustpilot

Ce dossier contient les scripts pour effectuer le scraping massif de reviews Trustpilot avec la stratégie multi-filtres.

## 📋 Scripts Disponibles

### 1. `test_mass_scraping.py` - Script de Test
**Objectif**: Tester le scraping sur 3 entreprises avec ~1000 reviews chacune

```bash
cd etl_elt
python scripts/test_mass_scraping.py
```

**Entreprises testées**:
- apple.com
- amazon.com  
- booking.com

**Configuration**:
- Max reviews: 1000 par entreprise
- Délai: 1.5s entre pages
- Stratégie: Multi-filtres (5★ → 1★)

**Sorties**:
- `data/test/{company}_test.json` - Reviews scrapées
- `data/test/test_report_{timestamp}.json` - Rapport du test

---

### 2. `mass_scraping.py` - Script de Production
**Objectif**: Scraper 60+ entreprises avec 10000+ reviews chacune

```bash
cd etl_elt
python scripts/mass_scraping.py
```

**Entreprises couvertes** (60+):

#### E-commerce & Retail
- amazon.com, amazon.co.uk, ebay.com, aliexpress.com
- wish.com, etsy.com, walmart.com, target.com

#### Tech
- apple.com, microsoft.com, google.com, samsung.com
- dell.com, hp.com

#### Services & Apps
- facebook.com, instagram.com, twitter.com, tiktok.com
- netflix.com, spotify.com, zoom.us, paypal.com

#### Travel & Transport
- booking.com, airbnb.com, expedia.com, tripadvisor.com
- uber.com, lyft.com, ryanair.com

#### Fashion & Lifestyle
- asos.com, zara.com, hm.com, nike.com, adidas.com

#### Food Delivery
- ubereats.com, deliveroo.com, doordash.com

#### Telecom & Utilities
- verizon.com, att.com, t-mobile.com

#### Finance
- revolut.com, n26.com, coinbase.com

#### France Spécifique
- showroomprive.com, vinted.fr, leboncoin.fr
- cdiscount.com, fnac.com, sncf.com
- orange.fr, freemobile.fr, bouyguestelecom.fr

**Configuration**:
- Max reviews: 10000 par entreprise
- Délai: 2.0s entre pages
- Pause: 5-10s entre entreprises
- Stratégie: Multi-filtres (5★ → 1★)

**Sorties**:
- `data/raw/{company}_reviews.json` - Reviews scrapées
- `data/scraping_report_{timestamp}.json` - Rapport global
- `logs/mass_scraping.log` - Logs détaillés

---

## 🔄 Stratégie Multi-Filtres

### Pourquoi ?
Trustpilot limite la pagination à ~200 pages (~2000 reviews) en affichage standard.

### Solution
Scraper séparément par note d'étoiles :
1. 5★ reviews (jusqu'à ~200 pages)
2. 4★ reviews (jusqu'à ~200 pages)
3. 3★ reviews (jusqu'à ~200 pages)
4. 2★ reviews (jusqu'à ~200 pages)
5. 1★ reviews (jusqu'à ~200 pages)

**Total**: ~10000 reviews possibles (5 × 2000)

### Déduplication
Les reviews sont automatiquement dédupliquées par `review_id` unique.

---

## 📊 Données Capturées

Pour chaque review :
- **Identifiants**: review_id, review_link
- **Entreprise**: company_name
- **Reviewer**: reviewer_name, reviewer_review_count
- **Dates**: review_date (absolute), review_date_relative
- **Scores**: stars, rating_score (0-10)
- **Contenu**: review_title, review_text
- **Réponses**: company_replied (bool), company_reply_text, company_reply_date

Pour chaque entreprise :
- company_name, trust_score, total_reviews
- categories, website, contact_info

---

## ⏱️ Temps Estimé

### Test (3 entreprises × 1000 reviews)
- Durée: ~30-45 minutes
- Reviews: ~3000 total

### Production (60 entreprises × 10000 reviews)
- Durée: ~30-40 heures
- Reviews: ~600,000 total
- Recommandation: Lancer la nuit ou en weekend

---

## 🛠️ Dépannage

### Erreur "Module not found"
```bash
cd etl_elt
python -m pip install -r requirements.txt
```

### Erreur de connexion
- Vérifier la connexion internet
- Attendre quelques minutes (possibilité de rate limiting)
- Augmenter le délai dans le script

### Scraping incomplet
- Le script reprend automatiquement si interrompu
- Vérifier les logs dans `logs/mass_scraping.log`
- Relancer le script, il skippe les entreprises déjà complétées

---

## 📁 Structure des Données

```
data/
├── test/                          # Résultats de test
│   ├── apple_com_test.json
│   ├── amazon_com_test.json
│   └── test_report_*.json
├── raw/                           # Résultats production
│   ├── apple_com_reviews.json
│   ├── amazon_com_reviews.json
│   └── ...
└── scraping_report_*.json        # Rapports globaux

logs/
└── mass_scraping.log             # Logs détaillés
```

---

## 🚦 Workflow Recommandé

1. **Test d'abord**
   ```bash
   python scripts/test_mass_scraping.py
   ```
   Vérifier que tout fonctionne sur 3 entreprises

2. **Vérifier les résultats**
   ```bash
   # Explorer les fichiers JSON générés
   ls data/test/
   ```

3. **Lancer la production**
   ```bash
   python scripts/mass_scraping.py
   ```
   Laisser tourner pendant 30-40h

4. **Monitorer la progression**
   ```bash
   # Voir les logs en temps réel
   Get-Content logs/mass_scraping.log -Wait -Tail 50
   
   # Compter les fichiers générés
   (Get-ChildItem data/raw/*.json).Count
   ```

---

## 📌 Notes Importantes

- **Rate Limiting**: Le script respecte un délai de 2s entre pages et 5-10s entre entreprises
- **Reprise**: Si interrompu (Ctrl+C), relancer le script - il reprend où il s'est arrêté
- **Stockage**: Prévoir ~2-3 GB d'espace disque pour 600k reviews
- **Éthique**: Respecter les conditions d'utilisation de Trustpilot

---

## 🔮 Prochaines Étapes

Après le scraping :

1. **Nettoyage des données**
   - Normalisation des dates
   - Détection de langue
   - Suppression des doublons

2. **Analyse exploratoire**
   - Distribution des notes
   - Tendances temporelles
   - Analyse de sentiment

3. **Modèle ML**
   - Prédiction de satisfaction
   - Classification de sentiment
   - Détection de thèmes

4. **Orchestration Airflow**
   - Scraping automatique quotidien
   - Pipeline ETL complet
   - Alertes et monitoring
