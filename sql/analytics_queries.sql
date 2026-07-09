-- Top 20 requested skills
SELECT TOP 20
    skill_name,
    COUNT(*) AS job_count
FROM dbo.job_ad_skills
GROUP BY skill_name
ORDER BY job_count DESC;

-- Number of jobs by city
SELECT
    city,
    COUNT(*) AS job_count
FROM dbo.job_ads
WHERE city IS NOT NULL
GROUP BY city
ORDER BY job_count DESC;

-- Number of jobs by employer
SELECT
    employer_name,
    COUNT(*) AS job_count
FROM dbo.job_ads
WHERE employer_name IS NOT NULL
GROUP BY employer_name
ORDER BY job_count DESC;

-- Number of jobs by occupation
SELECT
    occupation,
    COUNT(*) AS job_count
FROM dbo.job_ads
WHERE occupation IS NOT NULL
GROUP BY occupation
ORDER BY job_count DESC;

-- Number of jobs by employment type
SELECT
    employment_type,
    COUNT(*) AS job_count
FROM dbo.job_ads
WHERE employment_type IS NOT NULL
GROUP BY employment_type
ORDER BY job_count DESC;

-- Python/SQL/Azure/Machine Learning skill demand
SELECT
    CASE
        WHEN LOWER(skill_name) LIKE '%python%' THEN 'Python'
        WHEN LOWER(skill_name) LIKE '%sql%' THEN 'SQL'
        WHEN LOWER(skill_name) LIKE '%azure%' THEN 'Azure'
        WHEN LOWER(skill_name) LIKE '%machine learning%'
            OR LOWER(skill_name) LIKE '%maskininlärning%' THEN 'Machine Learning'
    END AS skill_group,
    COUNT(DISTINCT job_id) AS job_count
FROM dbo.job_ad_skills
WHERE LOWER(skill_name) LIKE '%python%'
    OR LOWER(skill_name) LIKE '%sql%'
    OR LOWER(skill_name) LIKE '%azure%'
    OR LOWER(skill_name) LIKE '%machine learning%'
    OR LOWER(skill_name) LIKE '%maskininlärning%'
GROUP BY
    CASE
        WHEN LOWER(skill_name) LIKE '%python%' THEN 'Python'
        WHEN LOWER(skill_name) LIKE '%sql%' THEN 'SQL'
        WHEN LOWER(skill_name) LIKE '%azure%' THEN 'Azure'
        WHEN LOWER(skill_name) LIKE '%machine learning%'
            OR LOWER(skill_name) LIKE '%maskininlärning%' THEN 'Machine Learning'
    END
ORDER BY job_count DESC;
