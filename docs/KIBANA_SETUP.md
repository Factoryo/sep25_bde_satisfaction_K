# Configuration Kibana pour Trustpilot Reviews

## 1. Créer l'Index Pattern

Une fois les données chargées dans Elasticsearch, créer l'index pattern dans Kibana:

1. Ouvrir Kibana: http://localhost:5601
2. Aller dans **Stack Management** > **Index Patterns**
3. Cliquer sur **Create index pattern**
4. Entrer `trustpilot_reviews` comme pattern
5. Sélectionner `date` comme Time field
6. Cliquer sur **Create index pattern**

## 2. Visualisations à créer

### 2.1 Metric: Total des avis
- **Type**: Metric
- **Aggregation**: Count
- **Titre**: "Total des avis"

### 2.2 Metric: Note moyenne
- **Type**: Metric
- **Aggregation**: Average of rating
- **Titre**: "Note moyenne"

### 2.3 Pie Chart: Distribution des notes
- **Type**: Pie
- **Buckets**: 
  - Aggregation: Terms
  - Field: rating
  - Size: 5
- **Metrics**: Count
- **Titre**: "Distribution des notes (étoiles)"

### 2.4 Bar Chart: Avis par entreprise (Top 10)
- **Type**: Vertical Bar
- **X-axis**: 
  - Aggregation: Terms
  - Field: company_name.keyword
  - Size: 10
  - Order: Metric - Count (Descending)
- **Y-axis**: Count
- **Titre**: "Top 10 entreprises par nombre d'avis"

### 2.5 Line Chart: Évolution des avis dans le temps
- **Type**: Line
- **X-axis**: 
  - Aggregation: Date Histogram
  - Field: date
  - Interval: Monthly
- **Y-axis**: Count
- **Titre**: "Évolution du nombre d'avis par mois"

### 2.6 Tag Cloud: Reviewers les plus actifs
- **Type**: Tag Cloud
- **Buckets**:
  - Aggregation: Terms
  - Field: reviewer_name.keyword
  - Size: 20
- **Titre**: "Reviewers les plus actifs"

### 2.7 Data Table: Derniers avis
- **Type**: Data Table
- **Buckets**:
  - Aggregation: Date Histogram
  - Field: date
  - Interval: Daily
- **Split rows**: Terms on company_name.keyword
- **Metrics**: Count, Average of rating
- **Titre**: "Activité récente par entreprise"

### 2.8 Horizontal Bar: Notes moyennes par entreprise
- **Type**: Horizontal Bar
- **Y-axis**:
  - Aggregation: Terms
  - Field: company_name.keyword
  - Size: 15
- **X-axis**: Average of rating
- **Titre**: "Note moyenne par entreprise (Top 15)"

### 2.9 Heat Map: Avis par jour de la semaine et heure
- **Type**: Heat Map
- **Y-axis**: 
  - Aggregation: Date Histogram
  - Field: date
  - Interval: Day of week
- **X-axis**:
  - Aggregation: Date Histogram
  - Field: date
  - Interval: Hour
- **Metrics**: Count
- **Titre**: "Activité des avis (jour/heure)"

### 2.10 Goal: Pourcentage d'avis positifs
- **Type**: Goal
- **Aggregation**: 
  - Filters:
    - Filter 1: rating >= 4
- **Goal value**: Total count (tous les avis)
- **Titre**: "% avis positifs (4-5 étoiles)"

## 3. Créer le Dashboard

1. Aller dans **Dashboard** > **Create dashboard**
2. Cliquer sur **Add**
3. Sélectionner toutes les visualisations créées ci-dessus
4. Organiser les visualisations:
   - Ligne 1: Metrics (Total avis, Note moyenne, % positifs)
   - Ligne 2: Distribution notes (Pie) + Top 10 entreprises (Bar)
   - Ligne 3: Évolution temporelle (Line) + Notes moyennes (Horizontal Bar)
   - Ligne 4: Table des derniers avis (Data Table)
   - Ligne 5: Tag Cloud (Reviewers actifs) + Heat Map
5. Sauvegarder le dashboard: **"Trustpilot Reviews Dashboard"**

## 4. Requêtes Kibana utiles (Dev Tools)

### 4.1 Rechercher tous les avis d'une entreprise
```json
GET trustpilot_reviews/_search
{
  "query": {
    "match": {
      "company_name": "Apple"
    }
  },
  "sort": [
    {"date": "desc"}
  ],
  "size": 100
}
```

### 4.2 Avis négatifs (1-2 étoiles)
```json
GET trustpilot_reviews/_search
{
  "query": {
    "range": {
      "rating": {
        "lte": 2
      }
    }
  },
  "sort": [
    {"date": "desc"}
  ]
}
```

### 4.3 Avis avec réponse de l'entreprise
```json
GET trustpilot_reviews/_search
{
  "query": {
    "exists": {
      "field": "company_reply.content"
    }
  },
  "sort": [
    {"date": "desc"}
  ]
}
```

### 4.4 Recherche full-text dans le contenu
```json
GET trustpilot_reviews/_search
{
  "query": {
    "multi_match": {
      "query": "livraison rapide service client",
      "fields": ["title^2", "content"]
    }
  },
  "highlight": {
    "fields": {
      "content": {},
      "title": {}
    }
  }
}
```

### 4.5 Agrégation: Note moyenne par entreprise
```json
GET trustpilot_reviews/_search
{
  "size": 0,
  "aggs": {
    "companies": {
      "terms": {
        "field": "company_name.keyword",
        "size": 20
      },
      "aggs": {
        "avg_rating": {
          "avg": {
            "field": "rating"
          }
        },
        "total_reviews": {
          "value_count": {
            "field": "rating"
          }
        }
      }
    }
  }
}
```

### 4.6 Agrégation: Évolution mensuelle
```json
GET trustpilot_reviews/_search
{
  "size": 0,
  "aggs": {
    "reviews_over_time": {
      "date_histogram": {
        "field": "date",
        "calendar_interval": "month"
      },
      "aggs": {
        "avg_rating": {
          "avg": {
            "field": "rating"
          }
        }
      }
    }
  }
}
```

### 4.7 Reviewers les plus actifs
```json
GET trustpilot_reviews/_search
{
  "size": 0,
  "aggs": {
    "top_reviewers": {
      "terms": {
        "field": "reviewer_name.keyword",
        "size": 50,
        "order": {
          "_count": "desc"
        }
      },
      "aggs": {
        "avg_given_rating": {
          "avg": {
            "field": "rating"
          }
        },
        "total_reviews_count": {
          "avg": {
            "field": "reviewer_reviews_count"
          }
        }
      }
    }
  }
}
```

### 4.8 Distribution des notes par entreprise
```json
GET trustpilot_reviews/_search
{
  "size": 0,
  "aggs": {
    "companies": {
      "terms": {
        "field": "company_name.keyword",
        "size": 10
      },
      "aggs": {
        "rating_distribution": {
          "terms": {
            "field": "rating",
            "size": 5
          }
        }
      }
    }
  }
}
```

### 4.9 Taux de réponse des entreprises
```json
GET trustpilot_reviews/_search
{
  "size": 0,
  "aggs": {
    "companies": {
      "terms": {
        "field": "company_name.keyword",
        "size": 20
      },
      "aggs": {
        "total": {
          "value_count": {
            "field": "company_name.keyword"
          }
        },
        "with_reply": {
          "filter": {
            "exists": {
              "field": "company_reply.content"
            }
          }
        },
        "reply_rate": {
          "bucket_script": {
            "buckets_path": {
              "replied": "with_reply>_count",
              "total": "total"
            },
            "script": "params.replied / params.total * 100"
          }
        }
      }
    }
  }
}
```

### 4.10 Sentiment: Ratio avis positifs/négatifs
```json
GET trustpilot_reviews/_search
{
  "size": 0,
  "aggs": {
    "positive": {
      "filter": {
        "range": {
          "rating": {"gte": 4}
        }
      }
    },
    "negative": {
      "filter": {
        "range": {
          "rating": {"lte": 2}
        }
      }
    },
    "neutral": {
      "filter": {
        "term": {
          "rating": 3
        }
      }
    }
  }
}
```

## 5. Filtres recommandés pour le Dashboard

Ajouter ces filtres au dashboard pour une exploration interactive:

1. **Date Range**: Filtre temporel sur le champ `date`
2. **Company**: Dropdown sur `company_name.keyword`
3. **Rating**: Range slider (1-5)
4. **Has Reply**: Toggle sur existence de `company_reply.content`
5. **Reviewer Count**: Range sur `reviewer_reviews_count`

## 6. Alertes Kibana (Watcher)

### 6.1 Alerte: Pic d'avis négatifs
Créer une alerte qui se déclenche si plus de X avis négatifs (1-2 étoiles) sont postés en une journée.

### 6.2 Alerte: Nouvelle entreprise
Déclencher une notification quand une nouvelle entreprise apparaît dans l'index.

### 6.3 Alerte: Baisse de note moyenne
Si la note moyenne d'une entreprise baisse de plus de X% sur la semaine.

## 7. Index Lifecycle Management (ILM)

Configurer une politique ILM pour gérer automatiquement:
- Rollover après 30 jours ou 50GB
- Move to warm tier après 90 jours
- Delete après 2 ans

```json
PUT _ilm/policy/trustpilot_policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_age": "30d",
            "max_size": "50gb"
          }
        }
      },
      "warm": {
        "min_age": "90d",
        "actions": {
          "readonly": {}
        }
      },
      "delete": {
        "min_age": "730d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```
