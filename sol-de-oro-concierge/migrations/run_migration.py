import sys
import requests

PROJECT_REF = "fjzshpilzjtfjcouzzzz"


def run_sql(management_token: str, sql_path: str) -> None:
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()
    resp = requests.post(
        f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query",
        headers={"Authorization": f"Bearer {management_token}", "Content-Type": "application/json"},
        json={"query": sql},
        timeout=30,
    )
    print(resp.status_code, resp.text[:2000])
    resp.raise_for_status()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python run_migration.py <management_token> <ruta_sql>")
        sys.exit(1)
    run_sql(sys.argv[1], sys.argv[2])
