import os

folders = [
    "dashboard",
    "data_extract_load",
    "data_transformation",
    "data_transformation/models",
    "data_transformation/models/staging",
    "data_transformation/models/dim",
    "data_transformation/models/fact",
    "orchestration",
    "duck_pond",
    "IaC_terraform"
]

files = {
    "dashboard/app.py": "",
    "data_extract_load/load_job_ads.py": "",
    "data_transformation/dbt_project.yml": "",
    "data_transformation/profiles.yml": "",
    "data_transformation/models/staging/stg_job_ads.sql": "",
    "data_transformation/models/dim/dim_city.sql": "",
    "data_transformation/models/dim/dim_occupation.sql": "",
    "data_transformation/models/dim/dim_employment_type.sql": "",
    "data_transformation/models/fact/fct_job_ads.sql": "",
    "orchestration/definitions.py": "",
    "IaC_terraform/main.tf": "",
    "IaC_terraform/variables.tf": "",
    "IaC_terraform/outputs.tf": "",
    "docker-compose.yml": "",
    "dockerfile.dwh": "",
    "dockerfile.dashboard": "",
    "README.md": ""
}

print("🔧 Skapar projektstruktur...")

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"📁 Skapade mapp: {folder}")

# Create files
for file_path, content in files.items():
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📄 Skapade tom fil: {file_path}")

print("\n🎉 KLART! Din projektstruktur är nu skapad.")
print("Du kan nu börja klistra in koden i rätt filer.")
