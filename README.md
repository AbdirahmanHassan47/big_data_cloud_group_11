# HR Analytics – Cloud Deployment (Grupp 11)

Det här projektet bygger vidare på ett tidigare HR Analytics-arbete där vi hämtar platsannonser från JobTech API och analyserar dem.  
I denna version har lösningen flyttats till Azure med Docker-containers.

## Översikt

Projektet består av:

- **DLT** – hämtar och laddar jobbannonser
- **DuckDB** – lagring av data (litet datalager)
- **DBT** – transformerar och modellerar data
- **Dagster** – kör pipelinen och schemalägger körningar
- **Streamlit** – dashboard för analys
- **Docker + Azure Container Registry** – körning i molnet

Processen:
1. DLT hämtar annonser från JobTech API  
2. Data sparas i `duck_pond/job_ads.duckdb`  
3. DBT skapar dimensioner och faktatabell  
4. Streamlit läser från DuckDB och visar visualiseringar  
5. Allt körs i Azure via två containers (pipeline + dashboard)

---

## Deployment till Azure (kortfattat)

### 1. Bygg Docker-images

```bash
docker compose build


Det bygger:

hr-pipeline (Dagster + dlt + dbt)

dashboard (Streamlit)

2. Logga in på ACR
az acr login --name <ditt_acr_namn>

3. Pusha images
docker tag hr-pipeline:latest <ditt_acr_namn>.azurecr.io/hr-pipeline:latest
docker tag dashboard:latest <ditt_acr_namn>.azurecr.io/dashboard:latest

docker push <ditt_acr_namn>.azurecr.io/hr-pipeline:latest
docker push <ditt_acr_namn>.azurecr.io/dashboard:latest

4. Kör Dagster i Azure Container Instance

Starta en container i Azure Portal eller via CLI och ge miljövariablerna:

DUCKDB_PATH=/app/duck_pond/job_ads.duckdb

DBT_PROFILES_DIR=/app/data_transformation

Mounta även en Azure File Share till /app/duck_pond.

Dagster UI nås sedan via:

http://<container-ip>:3000


Kör “Materialize All” där för att fylla DuckDB med data.

5. Kör dashboard i Azure App Service

Starta en container baserad på:

<ditt_acr_namn>.azurecr.io/dashboard:latest


Env vars:

DUCKDB_PATH=/app/duck_pond/job_ads.duckdb

Mounta samma Azure File Share till /app/duck_pond.

Dashboarden nås sedan via App Service-URL:en.

Kostnad (ca per månad)

Antaganden:

Pipelinens ETL körs 1 gång per dag

Dashboarden är tillgänglig dygnet runt

Små Azure-resurser används

Resurs	Kostnad (USD/mån)
App Service	~65 $
Container Registry	~6 $
File Share (10 GB)	~0.5 $
Dagster (ACI 30 min/dag)	~1 $
Totalt	~72–75 $
Om Snowflake skulle användas istället
Resurs	Kostnad (USD/mån)
App Service	~65 $
ACR	~6 $
Dagster (ACI)	~1 $
Snowflake Warehouse	~15 $
Snowflake Storage	<1 $
Totalt	~88 $

DuckDB = billigast,
Snowflake = bättre prestanda och skalning men högre pris.

Projektstruktur (förenklad)
big_data_cloud_group_11/
├── dashboard/
├── data_extract_load/
├── data_transformation/
├── duck_pond/
├── orchestration/
├── dockerfile.dashboard
├── dockerfile.dwh
├── docker-compose.yml
└── README.md

Sammanfattning

Projektet visar hur en enkel HR-data pipeline kan köras i Azure med:

Dagster för ETL-orchestration

DuckDB som datalager

DBT som transformationslager

Streamlit som dashboard

Docker + ACR för deployment

En billig och lättkörd molnlösning för ett mindre analysprojekt.