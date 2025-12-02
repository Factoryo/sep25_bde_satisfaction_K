# Champs capturés par le scraper Trustpilot

## Vue d'ensemble
Le scraper récupère **tous les champs demandés** pour chaque avis.

## 📋 Liste complète des champs

### Identification
- `review_id` : ID unique de l'avis
- `review_url` : Lien vers le commentaire détaillé sur Trustpilot

### Entreprise
- `company_name` : Nom de l'entreprise (ajouté après scraping)
- `company_trustscore` : Score TrustPilot de l'entreprise
- `company_total_reviews` : Nombre total d'avis de l'entreprise

### Note et Score
- `stars` : Nombre d'étoiles (1-5) ⭐
- `rating` : Alias de `stars` (compatibilité)
- `score` : Score normalisé sur 10 (stars / 5 * 10)

### Contenu de l'avis
- `title` : Titre du commentaire
- `content` : Texte brut du commentaire (version complète)
- `comment_text` : Alias de `content`

### Date du commentaire
- `date_absolute` : Date absolue au format ISO (ex: "2025-11-22T20:35:13.000Z")
- `date` : Alias de `date_absolute`
- `date_relative` : Date relative (ex: "2 days ago", "Updated Nov 22, 2025")
- `date_text` : Alias de `date_relative`

### Auteur du commentaire
- `author_name` : Nom de la personne à l'origine du commentaire
- `reviewer_name` : Alias de `author_name`
- `author_review_count` : Nombre de commentaires de cette personne sur TrustPilot
- `reviewer_total_reviews` : Alias de `author_review_count`
- `author_location` : Localisation de l'auteur (si disponible)

### Réponse de l'entreprise
- `has_company_reply` : Boolean - Si l'entreprise a répondu (true/false)
- `company_replied` : Alias de `has_company_reply`
- `company_reply` : Texte de la réponse de l'entreprise
- `company_reply_text` : Alias de `company_reply`
- `company_reply_date_absolute` : Date de la réponse (format ISO)
- `company_reply_date` : Alias de `company_reply_date_absolute`
- `company_reply_date_relative` : Date relative de la réponse

### Informations supplémentaires
- `is_verified` : Boolean - Si l'avis est vérifié
- `experience_date_text` : Date d'expérience/achat (si mentionnée)
- `helpful_count` : Nombre de votes "utile"
- `scraped_at` : Timestamp de récupération des données

## 📊 Exemple de structure JSON

```json
{
  "review_id": "abc123",
  "review_url": "https://www.trustpilot.com/reviews/abc123",
  "company_name": "ShowRoom Privé",
  "stars": 5,
  "rating": 5,
  "score": 10.0,
  "title": "Excellent service!",
  "content": "J'ai été très satisfait de mon expérience...",
  "comment_text": "J'ai été très satisfait de mon expérience...",
  "date_absolute": "2025-11-22T20:35:13.000Z",
  "date": "2025-11-22T20:35:13.000Z",
  "date_relative": "2 days ago",
  "date_text": "2 days ago",
  "author_name": "Jean Dupont",
  "reviewer_name": "Jean Dupont",
  "author_review_count": 15,
  "reviewer_total_reviews": 15,
  "author_location": "France",
  "has_company_reply": true,
  "company_replied": true,
  "company_reply": "Merci pour votre retour positif!",
  "company_reply_text": "Merci pour votre retour positif!",
  "company_reply_date_absolute": "2025-11-23T10:00:00.000Z",
  "company_reply_date": "2025-11-23T10:00:00.000Z",
  "company_reply_date_relative": "1 day ago",
  "is_verified": true,
  "experience_date_text": "Date of experience: November 20, 2025",
  "helpful_count": 5,
  "scraped_at": "2025-12-01T18:00:00.123456"
}
```

## ✅ Checklist des exigences

- ✅ Nom de l'entreprise
- ✅ Nom de la personne à l'origine du commentaire
- ✅ Nombre de commentaires de cette personne sur TrustPilot
- ✅ Date du commentaire (absolue ET relative)
- ✅ Réponse de l'entreprise (si existante)
  - ✅ Date de la réponse
- ✅ Nombre d'étoiles
- ✅ Score
- ✅ Titre du commentaire
- ✅ Lien vers le commentaire détaillé
- ✅ Texte brut du commentaire

## 🚀 Utilisation

```python
from scrapers.trustpilot_reviews_scraper import TrustpilotReviewsScraper

scraper = TrustpilotReviewsScraper(delay=2.0)

# Scraper avec la stratégie multi-filtres (recommandé pour >10000 avis)
reviews = scraper.scrape_all_reviews(
    company_url="https://www.trustpilot.com/review/www.showroom.com",
    max_reviews=None,  # Tous les avis
    use_filters=True   # Utiliser les filtres par étoiles
)

# Sauvegarder
scraper.save_to_json(reviews, 'reviews.json')
scraper.save_to_jsonl(reviews, 'reviews.jsonl')
```
