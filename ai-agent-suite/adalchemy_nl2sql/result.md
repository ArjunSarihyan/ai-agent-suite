# Query Results

## Query:
```sql
SELECT * FROM adproduct WHERE condensed_name_full ILIKE '%Basketball Equipment%'; SELECT * FROM audience WHERE condensed_name_full ILIKE '%18-24%' OR condensed_name_full ILIKE '%25-34%' OR condensed_name_full ILIKE '%35-44%' OR condensed_name_full ILIKE '%Basketball%' OR condensed_name_full ILIKE '%Sports Betting%' OR condensed_name_full ILIKE '%Virtual Betting%'; SELECT * FROM content WHERE condensed_name_full ILIKE '%Basketball%' OR condensed_name_full ILIKE '%College Basketball%';
```

### Table: adproduct

| Unique_ID | Parent_ID | taxonomy_type | Name | Tier_1 | Tier_2 | Tier_3 | condensed_name_full |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1366 | 1361.0 | adproduct | Sports Betting | Gambling | Sports Betting |  | Sports Betting | Gambling | Sports Betting |
| 1367 | 1361.0 | adproduct | Virtual Betting | Gambling | Virtal Betting |  | Virtual Betting | Gambling | Virtal Betting |

### Table: audience

| Unique_ID | Parent_ID | taxonomy_type | Condensed_Name_(1st,_2nd,_Last_Tier) | Tier_1 | Tier_2 | Tier_3 | Tier_4 | Tier_5 | Tier_6 | Extension_Notes | condensed_name_full |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 614 | 607.0 | audience | Interest | Sports | Basketball | | Interest | Sports | Basketball |  |  |  |  | Interest | Sports | Basketball |  | |
| 622 | 620.0 | audience | Interest | Sports | College Basketball | | Interest | Sports | College Sports | College Basketball |  |  |  | Interest | Sports | College Sports | College Basketball | |
| 1621 | 1619.0 | audience | Purchase Intent* | Sporting Goods | Basketball Equipment | | Purchase Intent* | Sporting Goods | Athletics Equipment | Basketball Equipment |  |  | See *Purchase Intent Classification* Extension | Purchase Intent* | Sporting Goods | Athletics Equipment | Basketball Equipment | |

### Table: content

| Unique_ID | Parent | taxonomy_type | Name | Tier_1 | Tier_2 | Tier_3 | Tier_4 | Extension | Podcast_Genres | CTV_Genres | condensed_name_full |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 547 | 483 | content | Basketball | Sports | Basketball |  |  |  | Basketball |  | Basketball | Sports | Basketball |  |  | Basketball |
| 489 | 487 | content | College Basketball | Sports | College Sports | College Basketball |  |  |  |  | College Basketball | Sports | College Sports | College Basketball |  | |

