import json
from sqlalchemy import create_engine, text
import psycopg2

#Create a connection to RDS PostgreSQL using SQLAlchemy
rds_host = "apan5450-db.c4c9zjbismmc.us-east-1.rds.amazonaws.com"
rds_port = "5432"
rds_dbname = "apan5450"
rds_username = "postgres"
rds_password = "postgres"

connection = None
try:
    conn_url = f"postgresql://{rds_username}:{rds_password}@{rds_host}:{rds_port}/{rds_dbname}"
    engine = create_engine(conn_url)
    connection = engine.connect()
    print("Successfully connected to RDS PostgreSQL using SQLAlchemy!")
except Exception as e:
    print("Error: Unable to connect to RDS PostgreSQL using SQLAlchemy.")
    print(e)


# Function to search company 
def search_company(searchTerm):
    searchTerm = searchTerm.lower()
    likeSearchTerm = '%' + searchTerm + '%'
    # Query RDS to search for searchTerm in company_name in companies table
    query1 = text("SELECT * FROM companies WHERE company_name LIKE :company ORDER BY CASE WHEN company_name = :exactCompany THEN 1 ELSE 2 end, company_id LIMIT 20;")
    companies = connection.execute(query1, parameters=dict(company=likeSearchTerm, exactCompany=searchTerm))
    return companies.fetchall()

# Lambda handler
def lambda_handler(event, context):
    # Search for company
    company = event['queryStringParameters']['search']
    results = []

    for row in search_company(company):
      result_dict = {
        'id' : row.company_id,
        'company' : row.company_name,
        'industry' : row.industry,
        'country' : row.country
      }
      results.append(result_dict)
    result = {
        'results': results
    }
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }