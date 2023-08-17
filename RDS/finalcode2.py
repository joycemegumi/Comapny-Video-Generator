import pandas as pd
import psycopg2
from sqlalchemy import create_engine

def clean_and_insert_data_to_rds():
    # Replace these variables with your RDS connection details
    rds_host = "apan5450-db.c4c9zjbismmc.us-east-1.rds.amazonaws.com"
    rds_port = "5432"
    rds_dbname = "apan5450"
    rds_username = "postgres"
    rds_password = "postgres"

    # Import and clean data
    companies_og = pd.read_csv("/home/ec2-user/companies_sorted.csv")
    logos_og = pd.read_csv("/home/ec2-user/companies.csv")

    def extract_city(city_str):
        if isinstance(city_str, str):
            return city_str.split(',')[0]
        return city_str

    def clean_column_name(col_name):
        return col_name.lower().replace(' ', '_')

    columns_to_drop = ['domain', 'linkedin url', 'current employee estimate', 'total employee estimate']
    companies_df = companies_og.drop(columns=columns_to_drop)
    companies_df = companies_df.iloc[:, 1:]
    companies_df.reset_index(inplace=True)
    companies_df["index"] = companies_df["index"] + 1
    companies_df["city"] = companies_df["locality"].apply(extract_city)
    companies_df = companies_df.drop(columns="locality")
    companies_df = companies_df.rename(columns={"name": "company_name",
                                                "index": "company_id",
                                                "year founded": "year_founded"})
    companies_df = companies_df.rename(columns=clean_column_name)
    companies_df = companies_df[["company_id", "company_name", "year_founded", "industry", "size_range", "city", "country"]]
    for column in companies_df.select_dtypes(include='object').columns:
        companies_df[column] = companies_df[column].str.lower()
    companies_df = companies_df.dropna()

    columns_to_drop = ['ticker', 'industry', 'description', 'website', 'ceo', 'exchange', 'company name',
                    'market cap', 'sector', 'tag 1', 'tag 2', 'tag 3']
    logos_df = logos_og.drop(columns=columns_to_drop)
    logos_df = logos_df.dropna()
    for column in logos_df.select_dtypes(include='object').columns:
        logos_df[column] = logos_df[column].str.lower()
    logos_df = logos_df.rename(columns={"short name": "company_name", "logo": "file_name"})
    
    unique_logos_df = pd.merge(logos_df, companies_df[['company_id', 'company_name']], on='company_name', how='inner')
    unique_logos_df.reset_index(inplace=True)
    unique_logos_df["index"] = unique_logos_df["index"] + 1
    unique_logos_df = unique_logos_df.rename(columns={"index": "logo_id"})
    unique_logos_df = unique_logos_df[['logo_id', 'company_id', 'file_name']]

    # Create a connection to RDS PostgreSQL using SQLAlchemy
    try:
        conn_url = f"postgresql://{rds_username}:{rds_password}@{rds_host}:{rds_port}/{rds_dbname}"
        engine = create_engine(conn_url, fast_executemany=True)
        connection = engine.connect()
        print("Successfully connected to RDS PostgreSQL using SQLAlchemy!")
    except Exception as e:
        print("Error: Unable to connect to RDS PostgreSQL using SQLAlchemy.")
        print(e)
        return

    # Create tables in RDS PostgreSQL
    create_table_cmd = """
        CREATE TABLE IF NOT EXISTS companies (
            company_id      SERIAL PRIMARY KEY,
            company_name    VARCHAR(255) NOT NULL,
            year_founded    INTEGER NOT NULL,
            industry        VARCHAR(255) NOT NULL,
            size_range      VARCHAR(255) NOT NULL,
            city            VARCHAR(100) NOT NULL,
            country         VARCHAR(255) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS logos (
            logo_id         SERIAL PRIMARY KEY,
            company_id      INTEGER ,
            file_name       VARCHAR(300) NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies (company_id)
        );
        CREATE TABLE IF NOT EXISTS generated_videos (
            video_id        SERIAL PRIMARY KEY,
            company_id      INTEGER,
            video_url       VARCHAR(250),
	    external_id	   VARCHAR(100) NOT NULL,
            created_at      TIMESTAMP NOT NULL,
            theme           SMALLINT NOT NULL,
            music           SMALLINT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies (company_id)
        );
    """
    connection.execute(create_table_cmd)

    # Insert data into the tables
    companies_df.to_sql(name='companies', con=engine, if_exists='append', index=False, method='multi', chunksize=1000)
    unique_logos_df.to_sql(name='logos', con=engine, if_exists='append', index=False, method='multi')

    # Query RDS PostgreSQL to get counts
    query1 = """
        SELECT COUNT(DISTINCT company_id) AS unique_companies
        FROM companies
    """
    unique_companies = pd.read_sql(query1, con=engine)

    query2 = """
        SELECT COUNT(DISTINCT logo_id) AS unique_logos
        FROM logos
    """
    unique_logos = pd.read_sql(query2, con=engine)

    print("There are {} unique companies in the companies table.".format(unique_companies['unique_companies'][0]))
    print("There are {} unique logos in the logos table.".format(unique_logos['unique_logos'][0]))

    # Close connection
    connection.close()
    engine.dispose()

if __name__ == "__main__":
    clean_and_insert_data_to_rds()
