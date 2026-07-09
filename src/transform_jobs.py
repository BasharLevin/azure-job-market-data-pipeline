import json
from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_files():
    raw_files = list(RAW_DIR.glob("job_ads_*.json"))

    all_ads = []

    for file_path in raw_files:
        print(f"Reading: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        ads = data.get("hits", [])
        all_ads.extend(ads)

    return all_ads


def extract_job_ad_fields(ad):
    workplace = ad.get("workplace_address") or {}
    employer = ad.get("employer") or {}
    occupation = ad.get("occupation") or {}
    description = ad.get("description") or {}

    return {
        "job_id": ad.get("id"),
        "title": ad.get("headline"),
        "employer_name": employer.get("name"),
        "city": workplace.get("municipality"),
        "region": workplace.get("region"),
        "country": workplace.get("country"),
        "occupation": occupation.get("label"),
        "publication_date": ad.get("publication_date"),
        "application_deadline": ad.get("application_deadline"),
        "description": description.get("text"),
        "employment_type": (ad.get("employment_type") or {}).get("label"),
        "working_hours_type": (ad.get("working_hours_type") or {}).get("label"),
        "salary_type": (ad.get("salary_type") or {}).get("label"),
        "webpage_url": ad.get("webpage_url"),
    }


def extract_skill_rows(ad):
    """
    Extract skill relationships from one job ad.

    Returns rows like:
    job_id | skill
    """

    job_id = ad.get("id")

    # JobTech sometimes stores skills/concepts in this field
    must_have = ad.get("must_have") or {}
    nice_to_have = ad.get("nice_to_have") or {}

    skill_rows = []

    for skill in must_have.get("skills", []):
        skill_label = skill.get("label")

        if skill_label:
            skill_rows.append({
                "job_id": job_id,
                "skill_name": skill_label,
                "skill_type": "must_have"
            })

    for skill in nice_to_have.get("skills", []):
        skill_label = skill.get("label")

        if skill_label:
            skill_rows.append({
                "job_id": job_id,
                "skill_name": skill_label,
                "skill_type": "nice_to_have"
            })

    return skill_rows


def transform_ads(ads):
    job_rows = []
    skill_relation_rows = []

    for ad in ads:
        job_rows.append(extract_job_ad_fields(ad))
        skill_relation_rows.extend(extract_skill_rows(ad))

    job_ads_df = pd.DataFrame(job_rows)
    job_ads_df = job_ads_df.drop_duplicates(subset=["job_id"])

    job_ads_df["publication_date"] = pd.to_datetime(
        job_ads_df["publication_date"],
        errors="coerce"
    )

    job_ads_df["application_deadline"] = pd.to_datetime(
        job_ads_df["application_deadline"],
        errors="coerce"
    )

    job_ad_skills_df = pd.DataFrame(skill_relation_rows)

    if not job_ad_skills_df.empty:
        job_ad_skills_df = job_ad_skills_df.drop_duplicates()

        skills_df = (
            job_ad_skills_df[["skill_name"]]
            .drop_duplicates()
            .sort_values("skill_name")
            .reset_index(drop=True)
        )

        skills_df["skill_id"] = skills_df.index + 1

        job_ad_skills_df = job_ad_skills_df.merge(
            skills_df,
            on="skill_name",
            how="left"
        )

        job_ad_skills_df = job_ad_skills_df[
            ["job_id", "skill_id", "skill_name", "skill_type"]
        ]

        skills_df = skills_df[["skill_id", "skill_name"]]

    else:
        skills_df = pd.DataFrame(columns=["skill_id", "skill_name"])
        job_ad_skills_df = pd.DataFrame(
            columns=["job_id", "skill_id", "skill_name", "skill_type"]
        )

    return job_ads_df, skills_df, job_ad_skills_df


def save_processed_data(job_ads_df, skills_df, job_ad_skills_df):
    job_ads_path = PROCESSED_DIR / "job_ads.csv"
    skills_path = PROCESSED_DIR / "skills.csv"
    job_ad_skills_path = PROCESSED_DIR / "job_ad_skills.csv"

    job_ads_df.to_csv(job_ads_path, index=False, encoding="utf-8")
    skills_df.to_csv(skills_path, index=False, encoding="utf-8")
    job_ad_skills_df.to_csv(job_ad_skills_path, index=False, encoding="utf-8")

    print(f"Saved: {job_ads_path} | rows: {len(job_ads_df)}")
    print(f"Saved: {skills_path} | rows: {len(skills_df)}")
    print(f"Saved: {job_ad_skills_path} | rows: {len(job_ad_skills_df)}")


def main():
    ads = load_raw_files()

    if not ads:
        print("No raw job ads found. Run extract_jobs.py first.")
        return

    job_ads_df, skills_df, job_ad_skills_df = transform_ads(ads)

    save_processed_data(job_ads_df, skills_df, job_ad_skills_df)


if __name__ == "__main__":
    main()