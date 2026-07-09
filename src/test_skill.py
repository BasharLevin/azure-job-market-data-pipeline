import pandas as pd

job_ads = pd.read_csv("data/processed/job_ads.csv")
skills = pd.read_csv("data/processed/skills.csv")
job_ad_skills = pd.read_csv("data/processed/job_ad_skills.csv")

print(job_ads.head())
print(skills.head())
print(job_ad_skills.head())

print("Job ads:", job_ads.shape)
print("Skills:", skills.shape)
print("Job-skill links:", job_ad_skills.shape)