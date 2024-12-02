# Database Schema Documentation

## Current Tables Overview

This document outlines the schema of our PostgreSQL database tables, focusing on the SEMrush data collection.

### `public.domains`
**Purpose:** Central repository for domain names to ensure normalization across all tables.

| Column Name | Data Type        | Length | Nullable | Default                     | Description                           |
|-------------|------------------|--------|----------|-----------------------------|---------------------------------------|
| id          | SERIAL           | -      | NO       | nextval('domains_id_seq')   | Auto-incrementing identifier for each domain. Primary Key |
| domain      | VARCHAR          | 255    | YES      | -                           | The domain name. UNIQUE |

---

### `public.semrush_domain_metrics`
**Purpose:** Tracks various performance metrics for a domain over time.

| Column Name            | Data Type   | Length | Nullable | Default                     | Description                             |
|------------------------|-------------|--------|----------|-----------------------------|-----------------------------------------|
| id                     | INTEGER      | -      | NO       | nextval('semrush_domain_metrics_id_seq') | Unique identifier. Primary Key  |
| date                   | DATE         | -      | NO       | -                           | Date of the metric data                 |
| organic_traffic        | INTEGER      | -      | YES      | -                           | Estimated organic traffic               |
| paid_traffic           | INTEGER      | -      | YES      | -                           | Estimated paid traffic                  |
| organic_keywords       | INTEGER      | -      | YES      | -                           | Number of keywords driving organic traffic |
| paid_keywords          | INTEGER      | -      | YES      | -                           | Number of keywords used for paid ads    |
| organic_traffic_cost   | NUMERIC(10,2)| -      | YES      | -                           | Estimated cost of organic traffic if purchased through ads |
| paid_traffic_cost      | NUMERIC(10,2)| -      | YES      | -                           | Cost of paid traffic                    |
| domain_authority       | INTEGER      | -      | YES      | -                           | Domain's authority score                |
| backlink_count         | INTEGER      | -      | YES      | -                           | Number of backlinks to the domain       |
| referring_domains      | INTEGER      | -      | YES      | -                           | Number of unique domains referring to this domain |
| domain_id              | INTEGER      | -      | YES      | -                           | Reference to domains table              |
| created_at             | TIMESTAMP    | -      | YES      | CURRENT_TIMESTAMP           | Timestamp when the record was created   |

---

### `public.semrush_keyword_rankings`
**Purpose:** Tracks the rank of keywords over time.

| Column Name        | Data Type   | Length | Nullable | Default                     | Description                             |
|--------------------|-------------|--------|----------|-----------------------------|-----------------------------------------|
| id                 | INTEGER     | -      | NO       | nextval('semrush_keyword_rankings_id_seq') | Unique identifier. Primary Key |
| keyword            | VARCHAR     | 255    | NO       | -                           | The keyword                             |
| position           | INTEGER     | -      | YES      | -                           | Current position in SERPs                |
| previous_position  | INTEGER     | -      | YES      | -                           | Position in the previous check          |
| search_volume      | INTEGER     | -      | YES      | -                           | Keyword's search volume                 |
| url                | VARCHAR     | 512    | YES      | -                           | URL ranking for this keyword            |
| date               | DATE        | -      | NO       | -                           | Date of the ranking data                |
| created_at         | TIMESTAMP   | -      | YES      | CURRENT_TIMESTAMP           | Timestamp when the record was created   |

---

### `public.semrush_competitor_data`
**Purpose:** Stores competitor data from SEMrush.

| Column Name         | Data Type       | Length | Nullable | Default                     | Description                             |
|---------------------|-----------------|--------|----------|-----------------------------|-----------------------------------------|
| id                  | INTEGER         | -      | NO       | nextval('semrush_competitor_data_id_seq') | Unique identifier. Primary Key|
| competitor_domain   | VARCHAR         | 255    | -        | -                           | Links to the domains table via domain_id |
| keyword_count       | INTEGER         | -      | YES      | -                           | Number of keywords the competitor is ranking for |
| traffic_estimate    | NUMERIC(10,2)   | -      | YES      | -                           | Estimated monthly traffic for the competitor |
| market_share        | NUMERIC(5,2)    | -      | YES      | -                           | The competitor's market share in the industry |
| date                | DATE            | -      | NO       | -                           | The date when the data was recorded     |
| created_at          | TIMESTAMP       | -      | YES      | CURRENT_TIMESTAMP           | Timestamp when the record was created   |

---

### `public.semrush_keyword_data`
**Purpose:** Contains keyword performance data for specific domains.

| Column Name         | Data Type       | Length | Nullable | Default                     | Description                             |
|---------------------|-----------------|--------|----------|-----------------------------|-----------------------------------------|
| domain              | VARCHAR         | 255    | NO       | -                           | The domain associated with the keywords. Primary Key Part |
| keyword             | VARCHAR         | 255    | NO       | -                           | The keyword being tracked. Primary Key Part |
| date                | DATE            | -      | NO       | -                           | Date of the keyword data. Primary Key Part |
| position            | INTEGER         | -      | YES      | -                           | Current ranking position of the keyword |
| previous_position   | INTEGER         | -      | YES      | -                           | Previous ranking position of the keyword |
| position_change     | INTEGER         | -      | YES      | -                           | Change in rank from previous period     |
| search_volume       | INTEGER         | -      | YES      | -                           | Monthly search volume for the keyword   |
| keyword_difficulty  | INTEGER         | -      | YES      | -                           | Difficulty score of ranking for this keyword |
| cpc                 | NUMERIC(10,2)   | -      | YES      | -                           | Cost per click for the keyword in paid search |
| traffic_percentage  | NUMERIC(5,2)    | -      | YES      | -                           | Percentage of traffic this keyword might bring |
| traffic_cost        | NUMERIC(10,2)   | -      | YES      | -                           | Estimated traffic cost if acquired through ads |
| competitive_density | NUMERIC(5,2)    | -      | YES      | -                           | Density of competition for this keyword |
| search_intent       | VARCHAR         | 50     | YES      | -                           | The intent behind searches for this keyword |
| created_at          | TIMESTAMP       | -      | YES      | CURRENT_TIMESTAMP           | Timestamp when the record was created   |

---

### `public.semrush_competitor_metrics`
**Purpose:** Detailed metrics about how competitors compare to each other or to your own domain.

| Column Name                      | Data Type       | Length | Nullable | Default                     | Description                             |
|----------------------------------|-----------------|--------|----------|-----------------------------|-----------------------------------------|
| id                               | INTEGER         | -      | NO       | -                           | Unique identifier. Primary Key          |
| competitor_domain                | VARCHAR         | 255    | -        | -                           | Links to the domains table via domain_id |
| date                             | DATE            | -      | NO       | -                           | Date of the metrics                     |
| keyword_overlap_count            | INTEGER         | -      | YES      | -                           | Number of keywords where there is overlap between domains |
| common_keywords_count            | INTEGER         | -      | YES      | -                           | Count of common keywords between you and a competitor |
| keyword_gap_count                | INTEGER         | -      | YES      | -                           | Number of keywords where competitors rank but you don't |
| market_share_percentage          | NUMERIC(5,2)    | -      | YES      | -                           | Market share percentage                 |
| visibility_score                 | NUMERIC(5,2)    | -      | YES      | -                           | Visibility score based on SEMrush's criteria |
| authority_score                  | INTEGER         | -      | YES      | -                           | Authority score of the domain           |
| created_at                       | TIMESTAMP       | -      | YES      | CURRENT_TIMESTAMP           | Timestamp when the record was created   |

---

### `public.semrush_social_metrics`
**Purpose:** Social media metrics for domains.

| Column Name             | Data Type       | Length | Nullable | Default                     | Description                             |
|-------------------------|-----------------|--------|----------|-----------------------------|-----------------------------------------|
| id                      | INTEGER         | -      | NO       | -                           | Unique identifier. Primary Key          |
| date                    | DATE            | -      | NO       | -                           | Date of the metrics                     |
| platform                | VARCHAR         | 50     | -        | -                           | Social media platform (e.g., 'Twitter', 'Facebook') |
| followers               | INTEGER         | -      | YES      | -                           | Number of followers on this platform    |
| engagement_rate         | NUMERIC(5,2)    | -      | YES      | -                           | Engagement rate on the platform         |
| total_engagement        | INTEGER         | -      | YES      | -                           | Total engagement metrics                |
| posts_count             | INTEGER         | -      | YES      | -                           | Number of posts made                    |
| mentions_count          | INTEGER         | -      | YES      | -                           | Number of times the domain was mentioned|
| sentiment_score         | NUMERIC(3,2)    | -      | YES      | -                           | Sentiment analysis score                |
| created_at              | TIMESTAMP       | -      | YES      | CURRENT_TIMESTAMP           | Timestamp when the record was created   |

---

### `public.keyword_categories`
**Purpose:** Categorize keywords for better SEO strategy management.

| Column Name       | Data Type       | Length | Nullable | Default                     | Description                             |
|-------------------|-----------------|--------|----------|-----------------------------|-----------------------------------------|
| id                | INTEGER         | -      | NO       | nextval('keyword_categories_id_seq') | Unique identifier. Primary Key |
| category_name     | VARCHAR         | 100    | NO       | -                           | The primary category the keyword falls into |
| subcategory       | VARCHAR         | 100    | YES      | -                           | Optional subcategory for more granular classification |
| keyword           | VARCHAR         | 255    | NO       | -                           | The keyword this entry describes        |
| priority          | INTEGER         | -      | YES      | 1                           | Priority of the keyword in SEO strategy |
| search_volume     | INTEGER         | -      | YES      | -                           | Monthly search volume of the keyword    |
| keyword_difficulty| INTEGER         | -      | YES      | -                           | Estimated difficulty in ranking for this keyword |
| current_rank      | INTEGER         | -      | YES      | -                           | Current position in search engine results |
| target_rank       | INTEGER         | -      | YES      | -                           | Target position in search engine results |
| notes             | TEXT            | -      | YES      | -                           | Additional notes about keyword's use or strategy |
| created_at        | TIMESTAMP       | -      | YES      | CURRENT_TIMESTAMP           | Timestamp when the record was created   |

## Table Relationships

- `semrush_domain_metrics.domain_id` → `domains.id`
- `semrush_keyword_data.domain` → `domains.domain`
- `semrush_competitor_metrics.competitor_domain` → `domains.domain`
- `semrush_competitor_data.competitor_domain` → `domains.domain`
- Note: `keyword_categories` does not have direct foreign key relationships to other tables in the schema provided, but could be linked to `semrush_keyword_data` through the `keyword` field if needed.

## Usage Notes

- All tables include a `created_at` timestamp that defaults to `CURRENT_TIMESTAMP`.
- The `domains` table serves as the central reference for all domain-related data.
- Most metrics tables include a `date` field for time-series analysis.
- Competitor and domain metrics are tracked separately for granular analysis.
- The `keyword_categories` table allows for a structured approach to keyword management, enabling categorization which can aid in SEO strategy planning.

## SEMrush API Integration Notes

The following API endpoints should be integrated for complete data collection:

- **Domain Analytics**: 
  - Organic Research
  - Backlinks
  - Traffic Analytics

- **Competitive Analysis**: 
  - Domain vs. Domain
  - Keyword Gap

- **Social Media Tracking**: 
  - Social Media Tracker

- **Rankings**: 
  - Position Tracking

Implementation priority should be based on business needs and API limitations.
