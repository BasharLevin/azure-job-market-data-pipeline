# Power BI Dashboard Plan

## Dashboard Goal

Create a Power BI dashboard that presents Swedish tech job market insights from the Azure SQL Database tables created by the pipeline. The dashboard should be clear, business-friendly, and suitable for portfolio screenshots.

## Data Source

- Source: Azure SQL Database
- Tables:
  - `job_ads`
  - `skills`
  - `job_ad_skills`

## Suggested Relationships

Create these relationships in the Power BI model:

```text
job_ads.job_id -> job_ad_skills.job_id
skills.skill_id -> job_ad_skills.skill_id
```

Recommended relationship setup:

- `job_ads` to `job_ad_skills`: one-to-many
- `skills` to `job_ad_skills`: one-to-many
- Cross-filter direction: single direction from dimension tables to bridge table

## Page 1: Job Market Overview

Purpose: Give a high-level view of the current Swedish tech job market.

### Key Metrics

- Total job ads
- Number of unique employers
- Number of unique cities
- Number of unique occupations
- Most recent publication date

### Suggested Visuals

- Card: Total job ads
- Card: Unique employers
- Card: Unique cities
- Bar chart: Jobs by city
- Bar chart: Jobs by occupation
- Donut chart or bar chart: Jobs by employment type
- Line chart or column chart: Job ads by publication date
- Table: Recent job ads with title, employer, city, occupation, and publication date

### Useful Fields

- `job_ads.job_id`
- `job_ads.title`
- `job_ads.employer_name`
- `job_ads.city`
- `job_ads.region`
- `job_ads.occupation`
- `job_ads.employment_type`
- `job_ads.publication_date`

## Page 2: Skills Demand

Purpose: Show which technical skills are most requested and how demand differs across roles.

### Key Metrics

- Total skill mentions
- Number of unique skills
- Top requested skill
- Demand for Python, SQL, Azure, and Machine Learning
- Must-have vs nice-to-have skill split

### Suggested Visuals

- Bar chart: Top requested skills
- Stacked bar chart: Must-have vs nice-to-have skills
- Card group: Python demand, SQL demand, Azure demand, Machine Learning demand
- Matrix: Skills by occupation
- Bar chart: Top skills filtered by selected occupation
- Slicer: Skill type
- Slicer: Occupation

### Useful Fields

- `skills.skill_id`
- `skills.skill_name`
- `job_ad_skills.job_id`
- `job_ad_skills.skill_name`
- `job_ad_skills.skill_type`
- `job_ads.occupation`

### Suggested Skill Grouping

Create a calculated column or Power Query grouping for important skill categories:

```text
Python
SQL
Azure
Machine Learning
Other
```

This can be used to compare demand for core data engineering and machine learning skills.

## Page 3: Employers and Locations

Purpose: Highlight hiring companies and geographic job market patterns.

### Key Metrics

- Top employer by number of job ads
- Top city by number of job ads
- Top region by number of job ads
- Number of employers hiring for selected skills

### Suggested Visuals

- Bar chart: Top employers by number of ads
- Map visual: Job ads by city or region
- Bar chart: Job ads by region
- Matrix: Employer skill demand
- Table: Employers with job count, city, region, and most requested skills
- Slicer: City
- Slicer: Region
- Slicer: Skill name

### Useful Fields

- `job_ads.employer_name`
- `job_ads.city`
- `job_ads.region`
- `job_ads.job_id`
- `job_ad_skills.skill_name`
- `job_ad_skills.skill_type`

## Suggested Measures

```DAX
Total Job Ads = DISTINCTCOUNT(job_ads[job_id])

Unique Employers = DISTINCTCOUNT(job_ads[employer_name])

Unique Cities = DISTINCTCOUNT(job_ads[city])

Unique Skills = DISTINCTCOUNT(skills[skill_id])

Skill Mentions = COUNTROWS(job_ad_skills)
```

## Screenshot Notes for README

Add dashboard screenshots to the README after the Power BI report is built.

Suggested screenshots:

- Full dashboard screenshot of the Job Market Overview page
- Skills Demand page showing top skills and must-have vs nice-to-have split
- Employers and Locations page showing top employers and location breakdown
- Optional screenshot of the Power BI model relationships view

Recommended README placement:

- Add a `Dashboard Preview` section after the architecture or analytics section.
- Include one main screenshot and two smaller supporting screenshots.
- Use short captions that explain the business insight shown in each screenshot.

## Portfolio Presentation Notes

- Keep visual titles clear and business-focused.
- Use consistent colors for skill categories across pages.
- Prefer clean bar charts and tables over overly complex visuals.
- Add slicers for city, occupation, employer, and skill type.
- Make sure every page answers a specific question about the job market.
