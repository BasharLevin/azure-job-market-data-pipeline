IF OBJECT_ID('dbo.job_ad_skills', 'U') IS NOT NULL
    DROP TABLE dbo.job_ad_skills;

IF OBJECT_ID('dbo.skills', 'U') IS NOT NULL
    DROP TABLE dbo.skills;

IF OBJECT_ID('dbo.job_ads', 'U') IS NOT NULL
    DROP TABLE dbo.job_ads;

CREATE TABLE dbo.job_ads (
    job_id BIGINT NOT NULL PRIMARY KEY,
    title NVARCHAR(500) NULL,
    employer_name NVARCHAR(500) NULL,
    city NVARCHAR(200) NULL,
    region NVARCHAR(200) NULL,
    country NVARCHAR(100) NULL,
    occupation NVARCHAR(300) NULL,
    publication_date DATETIME2 NULL,
    application_deadline DATETIME2 NULL,
    description NVARCHAR(MAX) NULL,
    employment_type NVARCHAR(300) NULL,
    working_hours_type NVARCHAR(200) NULL,
    salary_type NVARCHAR(300) NULL,
    webpage_url NVARCHAR(1000) NULL
);

CREATE TABLE dbo.skills (
    skill_id INT NOT NULL PRIMARY KEY,
    skill_name NVARCHAR(500) NOT NULL
);

CREATE TABLE dbo.job_ad_skills (
    job_id BIGINT NOT NULL,
    skill_id INT NOT NULL,
    skill_name NVARCHAR(500) NULL,
    skill_type NVARCHAR(100) NOT NULL,
    CONSTRAINT pk_job_ad_skills PRIMARY KEY (job_id, skill_id, skill_type),
    CONSTRAINT fk_job_ad_skills_job_ads FOREIGN KEY (job_id)
        REFERENCES dbo.job_ads(job_id),
    CONSTRAINT fk_job_ad_skills_skills FOREIGN KEY (skill_id)
        REFERENCES dbo.skills(skill_id)
);
