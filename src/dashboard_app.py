import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


REQUIRED_ENV_VARS = {
    "AZURE_SQL_SERVER": "your_server_name.database.windows.net",
    "AZURE_SQL_DATABASE": "your_database_name",
    "AZURE_SQL_USERNAME": "your_username",
    "AZURE_SQL_PASSWORD": "your_password",
    "AZURE_SQL_DRIVER": "",
}


def get_required_env_value(name, placeholder):
    value = os.getenv(name)

    if value is None or value.strip() == "":
        st.error(f"Missing required environment variable: {name}")
        return None

    if placeholder and value.strip() == placeholder:
        st.error(f"Please replace the placeholder value for {name} in your .env file.")
        return None

    return value


def load_sql_settings():
    settings = {}

    for name, placeholder in REQUIRED_ENV_VARS.items():
        value = get_required_env_value(name, placeholder)
        if value is None:
            return None
        settings[name] = value

    return settings


@st.cache_resource
def create_sql_engine(server, database, username, password, driver):
    connection_url = URL.create(
        "mssql+pyodbc",
        username=username,
        password=password,
        host=server,
        port=1433,
        database=database,
        query={
            "driver": driver,
            "Encrypt": "yes",
            "TrustServerCertificate": "no",
            "Connection Timeout": "60",
        },
    )

    return create_engine(connection_url)


def build_filter_clause(city, skill_type, occupation):
    filters = []
    params = {}

    if city != "All":
        filters.append("ja.city = :city")
        params["city"] = city

    if skill_type != "All":
        filters.append("jas.skill_type = :skill_type")
        params["skill_type"] = skill_type

    if occupation != "All":
        filters.append("ja.occupation = :occupation")
        params["occupation"] = occupation

    if not filters:
        return "", params

    return "WHERE " + " AND ".join(filters), params


def read_sql(engine, query, params=None):
    return pd.read_sql(text(query), engine, params=params or {})


@st.cache_data(ttl=300)
def load_filter_options(_engine):
    cities = read_sql(
        _engine,
        """
        SELECT DISTINCT city
        FROM dbo.job_ads
        WHERE city IS NOT NULL
        ORDER BY city
        """,
    )

    skill_types = read_sql(
        _engine,
        """
        SELECT DISTINCT skill_type
        FROM dbo.job_ad_skills
        WHERE skill_type IS NOT NULL
        ORDER BY skill_type
        """,
    )

    occupations = read_sql(
        _engine,
        """
        SELECT DISTINCT occupation
        FROM dbo.job_ads
        WHERE occupation IS NOT NULL
        ORDER BY occupation
        """,
    )

    return cities, skill_types, occupations


@st.cache_data(ttl=300)
def load_dashboard_data(_engine, city, skill_type, occupation):
    filter_clause, params = build_filter_clause(city, skill_type, occupation)

    kpis = read_sql(
        _engine,
        f"""
        SELECT
            COUNT(DISTINCT ja.job_id) AS total_job_ads,
            COUNT(DISTINCT jas.skill_id) AS total_unique_skills,
            COUNT(DISTINCT ja.employer_name) AS total_employers,
            COUNT(DISTINCT ja.city) AS total_cities
        FROM dbo.job_ads AS ja
        LEFT JOIN dbo.job_ad_skills AS jas
            ON ja.job_id = jas.job_id
        {filter_clause}
        """,
        params,
    )

    top_skills = read_sql(
        _engine,
        f"""
        SELECT TOP 20
            jas.skill_name,
            COUNT(DISTINCT ja.job_id) AS job_count
        FROM dbo.job_ads AS ja
        INNER JOIN dbo.job_ad_skills AS jas
            ON ja.job_id = jas.job_id
        {filter_clause}
        GROUP BY jas.skill_name
        ORDER BY job_count DESC
        """,
        params,
    )

    jobs_by_city = read_sql(
        _engine,
        f"""
        SELECT
            ja.city,
            COUNT(DISTINCT ja.job_id) AS job_count
        FROM dbo.job_ads AS ja
        LEFT JOIN dbo.job_ad_skills AS jas
            ON ja.job_id = jas.job_id
        {filter_clause}
        GROUP BY ja.city
        HAVING ja.city IS NOT NULL
        ORDER BY job_count DESC
        """,
        params,
    )

    jobs_by_employer = read_sql(
        _engine,
        f"""
        SELECT TOP 20
            ja.employer_name,
            COUNT(DISTINCT ja.job_id) AS job_count
        FROM dbo.job_ads AS ja
        LEFT JOIN dbo.job_ad_skills AS jas
            ON ja.job_id = jas.job_id
        {filter_clause}
        GROUP BY ja.employer_name
        HAVING ja.employer_name IS NOT NULL
        ORDER BY job_count DESC
        """,
        params,
    )

    jobs_by_occupation = read_sql(
        _engine,
        f"""
        SELECT
            ja.occupation,
            COUNT(DISTINCT ja.job_id) AS job_count
        FROM dbo.job_ads AS ja
        LEFT JOIN dbo.job_ad_skills AS jas
            ON ja.job_id = jas.job_id
        {filter_clause}
        GROUP BY ja.occupation
        HAVING ja.occupation IS NOT NULL
        ORDER BY job_count DESC
        """,
        params,
    )

    skill_types = read_sql(
        _engine,
        f"""
        SELECT
            jas.skill_type,
            COUNT(*) AS skill_count
        FROM dbo.job_ads AS ja
        INNER JOIN dbo.job_ad_skills AS jas
            ON ja.job_id = jas.job_id
        {filter_clause}
        GROUP BY jas.skill_type
        HAVING jas.skill_type IS NOT NULL
        ORDER BY skill_count DESC
        """,
        params,
    )

    job_ads = read_sql(
        _engine,
        f"""
        SELECT DISTINCT
            ja.title,
            ja.employer_name,
            ja.city,
            ja.occupation,
            ja.publication_date,
            ja.application_deadline,
            ja.webpage_url
        FROM dbo.job_ads AS ja
        LEFT JOIN dbo.job_ad_skills AS jas
            ON ja.job_id = jas.job_id
        {filter_clause}
        ORDER BY ja.publication_date DESC
        """,
        params,
    )

    return {
        "kpis": kpis,
        "top_skills": top_skills,
        "jobs_by_city": jobs_by_city,
        "jobs_by_employer": jobs_by_employer,
        "jobs_by_occupation": jobs_by_occupation,
        "skill_types": skill_types,
        "job_ads": job_ads,
    }


def show_bar_chart(dataframe, label_column, value_column):
    chart_data = dataframe.set_index(label_column)[value_column]
    st.bar_chart(chart_data)


def main():
    load_dotenv()

    st.set_page_config(
        page_title="Swedish Tech Job Market Analytics",
        layout="wide",
    )

    st.title("Swedish Tech Job Market Analytics")
    st.write(
        "This dashboard analyzes Swedish tech job postings collected from the "
        "JobTech API and loaded into Azure SQL Database."
    )

    settings = load_sql_settings()
    if settings is None:
        st.stop()

    try:
        engine = create_sql_engine(
            settings["AZURE_SQL_SERVER"],
            settings["AZURE_SQL_DATABASE"],
            settings["AZURE_SQL_USERNAME"],
            settings["AZURE_SQL_PASSWORD"],
            settings["AZURE_SQL_DRIVER"],
        )

        cities, skill_types, occupations = load_filter_options(engine)

        city_options = ["All"] + cities["city"].dropna().tolist()
        skill_type_options = ["All"] + skill_types["skill_type"].dropna().tolist()
        occupation_options = ["All"] + occupations["occupation"].dropna().tolist()

        st.sidebar.header("Filters")
        selected_city = st.sidebar.selectbox("City", city_options)
        selected_skill_type = st.sidebar.selectbox("Skill type", skill_type_options)
        selected_occupation = st.sidebar.selectbox("Occupation", occupation_options)

        data = load_dashboard_data(
            engine,
            selected_city,
            selected_skill_type,
            selected_occupation,
        )

    except Exception as error:
        st.error("Could not connect to Azure SQL Database or load dashboard data.")
        st.info("Check your .env SQL settings, Azure SQL firewall rules, and ODBC driver.")
        st.error(f"Error: {error}")
        st.stop()

    kpis = data["kpis"].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total job ads", int(kpis["total_job_ads"] or 0))
    col2.metric("Total unique skills", int(kpis["total_unique_skills"] or 0))
    col3.metric("Total employers", int(kpis["total_employers"] or 0))
    col4.metric("Total cities", int(kpis["total_cities"] or 0))

    st.subheader("Top 20 Requested Skills")
    show_bar_chart(data["top_skills"], "skill_name", "job_count")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Number of Jobs by City")
        show_bar_chart(data["jobs_by_city"], "city", "job_count")

        st.subheader("Number of Jobs by Occupation")
        show_bar_chart(data["jobs_by_occupation"], "occupation", "job_count")

    with col2:
        st.subheader("Number of Jobs by Employer")
        show_bar_chart(data["jobs_by_employer"], "employer_name", "job_count")

        st.subheader("Must-Have vs Nice-to-Have Skills")
        show_bar_chart(data["skill_types"], "skill_type", "skill_count")

    st.subheader("Job Ads")
    st.dataframe(
        data["job_ads"],
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()
