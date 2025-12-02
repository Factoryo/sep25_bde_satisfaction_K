-- ========================================
-- REQUÊTES SQL DE DÉMONSTRATION
-- Base de données: trustpilot_db (PostgreSQL)
-- ========================================

-- ========================================
-- 1. REQUÊTES DE BASE
-- ========================================

-- Lister toutes les entreprises
SELECT * FROM Entreprise LIMIT 10;

-- Compter le nombre total d'entreprises
SELECT COUNT(*) as total_entreprises FROM Entreprise;

-- Voir toutes les catégories disponibles
SELECT * FROM Category ORDER BY category_name;

-- Compter les entreprises par catégorie
SELECT 
    c.category_name,
    COUNT(e.entreprise_id) as nombre_entreprises
FROM Category c
LEFT JOIN Entreprise e ON c.category_id = e.category_id
GROUP BY c.category_name
ORDER BY nombre_entreprises DESC;


-- ========================================
-- 2. ANALYSE DES TRUSTSCORES
-- ========================================

-- Top 10 entreprises par TrustScore
SELECT 
    e.entreprise_name,
    r.trustscore,
    (r.five_star + r.four_star + r.three_star + r.two_star + r.one_star) as total_avis
FROM Entreprise e
JOIN Rating r ON e.entreprise_id = r.entreprise_id
ORDER BY r.trustscore DESC
LIMIT 10;

-- Statistiques globales des TrustScores
SELECT 
    COUNT(*) as nombre_entreprises,
    ROUND(AVG(trustscore)::numeric, 2) as trustscore_moyen,
    ROUND(MIN(trustscore)::numeric, 2) as trustscore_min,
    ROUND(MAX(trustscore)::numeric, 2) as trustscore_max,
    ROUND(STDDEV(trustscore)::numeric, 2) as ecart_type
FROM Rating;

-- Distribution des TrustScores par tranche
SELECT 
    CASE 
        WHEN trustscore >= 4.5 THEN 'Excellent (4.5-5.0)'
        WHEN trustscore >= 4.0 THEN 'Très bon (4.0-4.5)'
        WHEN trustscore >= 3.5 THEN 'Bon (3.5-4.0)'
        WHEN trustscore >= 3.0 THEN 'Moyen (3.0-3.5)'
        WHEN trustscore >= 2.0 THEN 'Médiocre (2.0-3.0)'
        ELSE 'Mauvais (< 2.0)'
    END as categorie_trustscore,
    COUNT(*) as nombre_entreprises,
    ROUND(AVG(trustscore)::numeric, 2) as trustscore_moyen
FROM Rating
GROUP BY categorie_trustscore
ORDER BY trustscore_moyen DESC;


-- ========================================
-- 3. ANALYSE DES AVIS (DISTRIBUTION ÉTOILES)
-- ========================================

-- Distribution globale des étoiles
SELECT 
    SUM(one_star) as total_1_etoile,
    SUM(two_star) as total_2_etoiles,
    SUM(three_star) as total_3_etoiles,
    SUM(four_star) as total_4_etoiles,
    SUM(five_star) as total_5_etoiles,
    SUM(one_star + two_star + three_star + four_star + five_star) as total_avis
FROM Rating;

-- Pourcentage de chaque type d'étoile
SELECT 
    ROUND((SUM(five_star)::numeric / SUM(one_star + two_star + three_star + four_star + five_star)) * 100, 2) as pct_5_etoiles,
    ROUND((SUM(four_star)::numeric / SUM(one_star + two_star + three_star + four_star + five_star)) * 100, 2) as pct_4_etoiles,
    ROUND((SUM(three_star)::numeric / SUM(one_star + two_star + three_star + four_star + five_star)) * 100, 2) as pct_3_etoiles,
    ROUND((SUM(two_star)::numeric / SUM(one_star + two_star + three_star + four_star + five_star)) * 100, 2) as pct_2_etoiles,
    ROUND((SUM(one_star)::numeric / SUM(one_star + two_star + three_star + four_star + five_star)) * 100, 2) as pct_1_etoile
FROM Rating;

-- Entreprises avec le plus d'avis négatifs (1-2 étoiles)
SELECT 
    e.entreprise_name,
    r.one_star + r.two_star as avis_negatifs,
    (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) as total_avis,
    ROUND(((r.one_star + r.two_star)::numeric / (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star)) * 100, 2) as pct_negatif,
    r.trustscore
FROM Entreprise e
JOIN Rating r ON e.entreprise_id = r.entreprise_id
WHERE (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) > 100
ORDER BY pct_negatif DESC
LIMIT 10;

-- Entreprises avec le plus d'avis positifs (4-5 étoiles)
SELECT 
    e.entreprise_name,
    r.four_star + r.five_star as avis_positifs,
    (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) as total_avis,
    ROUND(((r.four_star + r.five_star)::numeric / (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star)) * 100, 2) as pct_positif,
    r.trustscore
FROM Entreprise e
JOIN Rating r ON e.entreprise_id = r.entreprise_id
WHERE (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) > 100
ORDER BY pct_positif DESC
LIMIT 10;


-- ========================================
-- 4. ANALYSE PAR CATÉGORIE
-- ========================================

-- TrustScore moyen par catégorie
SELECT 
    c.category_name,
    COUNT(e.entreprise_id) as nombre_entreprises,
    ROUND(AVG(r.trustscore)::numeric, 2) as trustscore_moyen,
    SUM(r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) as total_avis
FROM Category c
JOIN Entreprise e ON c.category_id = e.category_id
JOIN Rating r ON e.entreprise_id = r.entreprise_id
GROUP BY c.category_name
ORDER BY trustscore_moyen DESC;

-- Meilleure entreprise de chaque catégorie
WITH RankedCompanies AS (
    SELECT 
        c.category_name,
        e.entreprise_name,
        r.trustscore,
        (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) as total_avis,
        ROW_NUMBER() OVER (PARTITION BY c.category_id ORDER BY r.trustscore DESC) as rank
    FROM Category c
    JOIN Entreprise e ON c.category_id = e.category_id
    JOIN Rating r ON e.entreprise_id = r.entreprise_id
)
SELECT 
    category_name,
    entreprise_name,
    trustscore,
    total_avis
FROM RankedCompanies
WHERE rank = 1
ORDER BY trustscore DESC;


-- ========================================
-- 5. ANALYSE GÉOGRAPHIQUE
-- ========================================

-- Entreprises par pays
SELECT 
    a.country,
    COUNT(e.entreprise_id) as nombre_entreprises,
    ROUND(AVG(r.trustscore)::numeric, 2) as trustscore_moyen
FROM Address a
JOIN Entreprise e ON a.entreprise_id = e.entreprise_id
JOIN Rating r ON e.entreprise_id = r.entreprise_id
WHERE a.country IS NOT NULL
GROUP BY a.country
ORDER BY nombre_entreprises DESC;

-- Entreprises par ville (Top 10)
SELECT 
    a.city,
    a.country,
    COUNT(e.entreprise_id) as nombre_entreprises,
    ROUND(AVG(r.trustscore)::numeric, 2) as trustscore_moyen
FROM Address a
JOIN Entreprise e ON a.entreprise_id = e.entreprise_id
JOIN Rating r ON e.entreprise_id = r.entreprise_id
WHERE a.city IS NOT NULL
GROUP BY a.city, a.country
ORDER BY nombre_entreprises DESC
LIMIT 10;


-- ========================================
-- 6. UTILISATION DES VUES
-- ========================================

-- Vue: all_company_raw_data
-- Toutes les informations des entreprises en un seul SELECT
SELECT * FROM all_company_raw_data LIMIT 10;

-- Vue: company_ratings
-- Vue simplifiée des ratings
SELECT * FROM company_ratings 
ORDER BY trustscore DESC 
LIMIT 10;


-- ========================================
-- 7. REQUÊTES AVANCÉES - CORRÉLATIONS
-- ========================================

-- Corrélation entre nombre d'avis et TrustScore
SELECT 
    CASE 
        WHEN total_avis < 100 THEN '0-100 avis'
        WHEN total_avis < 500 THEN '100-500 avis'
        WHEN total_avis < 1000 THEN '500-1000 avis'
        WHEN total_avis < 5000 THEN '1000-5000 avis'
        ELSE '5000+ avis'
    END as tranche_avis,
    COUNT(*) as nombre_entreprises,
    ROUND(AVG(trustscore)::numeric, 2) as trustscore_moyen,
    ROUND(MIN(trustscore)::numeric, 2) as trustscore_min,
    ROUND(MAX(trustscore)::numeric, 2) as trustscore_max
FROM (
    SELECT 
        e.entreprise_id,
        r.trustscore,
        (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) as total_avis
    FROM Entreprise e
    JOIN Rating r ON e.entreprise_id = r.entreprise_id
) as subquery
GROUP BY tranche_avis
ORDER BY 
    CASE tranche_avis
        WHEN '0-100 avis' THEN 1
        WHEN '100-500 avis' THEN 2
        WHEN '500-1000 avis' THEN 3
        WHEN '1000-5000 avis' THEN 4
        WHEN '5000+ avis' THEN 5
    END;

-- Entreprises avec écart important entre avis positifs et négatifs
SELECT 
    e.entreprise_name,
    r.five_star as avis_5_etoiles,
    r.one_star as avis_1_etoile,
    ABS(r.five_star - r.one_star) as ecart,
    r.trustscore,
    (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) as total_avis
FROM Entreprise e
JOIN Rating r ON e.entreprise_id = r.entreprise_id
WHERE (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) > 100
ORDER BY ecart DESC
LIMIT 20;


-- ========================================
-- 8. REQUÊTES D'EXPORT POUR ANALYSE
-- ========================================

-- Export complet pour analyse externe (CSV)
SELECT 
    e.entreprise_name,
    e.web_site,
    c.category_name,
    a.city,
    a.country,
    r.trustscore,
    r.one_star,
    r.two_star,
    r.three_star,
    r.four_star,
    r.five_star,
    (r.one_star + r.two_star + r.three_star + r.four_star + r.five_star) as total_avis,
    ROUND(((r.four_star + r.five_star)::numeric / NULLIF(r.one_star + r.two_star + r.three_star + r.four_star + r.five_star, 0)) * 100, 2) as pct_positif,
    ROUND(((r.one_star + r.two_star)::numeric / NULLIF(r.one_star + r.two_star + r.three_star + r.four_star + r.five_star, 0)) * 100, 2) as pct_negatif
FROM Entreprise e
LEFT JOIN Category c ON e.category_id = c.category_id
LEFT JOIN Address a ON e.entreprise_id = a.entreprise_id
LEFT JOIN Rating r ON e.entreprise_id = r.entreprise_id
ORDER BY r.trustscore DESC;


-- ========================================
-- 9. REQUÊTES DE MAINTENANCE
-- ========================================

-- Vérifier l'intégrité des données
SELECT 
    'Entreprises sans rating' as verification,
    COUNT(*) as nombre
FROM Entreprise e
LEFT JOIN Rating r ON e.entreprise_id = r.entreprise_id
WHERE r.entreprise_id IS NULL

UNION ALL

SELECT 
    'Entreprises sans catégorie' as verification,
    COUNT(*) as nombre
FROM Entreprise e
WHERE e.category_id IS NULL

UNION ALL

SELECT 
    'Entreprises sans adresse' as verification,
    COUNT(*) as nombre
FROM Entreprise e
LEFT JOIN Address a ON e.entreprise_id = a.entreprise_id
WHERE a.entreprise_id IS NULL;

-- Taille de la base de données
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
