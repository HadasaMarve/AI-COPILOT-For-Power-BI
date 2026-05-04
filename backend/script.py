
import os
import json
import re
import sys
import pandas as pd

dll_path = r"C:\Program Files\Microsoft.NET\ADOMD.NET\160"

sys.path.append(dll_path)
os.environ["PATH"] = dll_path + ";" + os.environ["PATH"]
from pyadomd import Pyadomd


############################################
# 1. מציאת visual.json לפי title
############################################

def find_visual_by_title(pbip_report_path, title):

    for root, dirs, files in os.walk(pbip_report_path):

        if "visual.json" in files:

            path = os.path.join(root, "visual.json")

            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)

                visual_title = None

                if "title" in data.get("visual", {}):
                    visual_title = data["visual"]["title"]

                elif "visualContainerObjects" in data.get("visual", {}):
                    objs = data["visual"]["visualContainerObjects"]
                    if "title" in objs:
                        visual_title = objs["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"]

                if visual_title:
                    visual_title = visual_title.replace("'", "")

                if visual_title == title:
                    return path

            except Exception:
                pass

    raise Exception("Visual not found")


############################################
# 2. שליפת fields
############################################
def extract_fields_recursive(node, results):

    if isinstance(node, dict):

        # זיהוי column רגיל
        if "Column" in node:

            col = node["Column"]

            try:
                table = col["Expression"]["SourceRef"]["Entity"]
                column = col["Property"]

                results.append(("column", table, column))

            except Exception:
                pass


        # זיהוי aggregation
        if "Aggregation" in node:

            agg = node["Aggregation"]

            try:
                column = agg["Expression"]["Column"]["Property"]
                table = agg["Expression"]["Column"]["Expression"]["SourceRef"]["Entity"]

                func_map = {
                    0: "SUM",
                    1: "AVG",
                    2: "MIN",
                    3: "MAX",
                    4: "COUNT"
                }

                func = func_map.get(agg.get("Function", 0), "SUM")

                results.append(("measure", table, column, func))

            except Exception:
                pass


        # המשך סריקה רקורסיבית
        for v in node.values():
            extract_fields_recursive(v, results)

    elif isinstance(node, list):

        for item in node:
            extract_fields_recursive(item, results)

def clean_fields(fields):

    measures = {(f[1], f[2]) for f in fields if f[0] == "measure"}

    cleaned = []

    for f in fields:

        if f[0] == "column":
            if (f[1], f[2]) in measures:
                continue

        cleaned.append(f)

    return cleaned


def extract_fields_from_visual(visual_path):

    with open(visual_path, encoding="utf-8") as f:
        data = json.load(f)

    results = []

    query_state = data.get("visual", {}).get("query", {}).get("queryState", {})

    for role in query_state.values():
        if isinstance(role, dict) and "projections" in role:
            extract_fields_recursive(role["projections"], results)
    results = list(set(results))

    return results


############################################
# 3. בניית DAX
############################################

def build_dax_query(fields):

    columns = []
    measures = []

    for f in fields:

        if f[0] == "column":
            columns.append(f"'{f[1]}'[{f[2]}]")

        elif f[0] == "measure":

            table, col, func = f[1], f[2], f[3]

            measures.append(
                f'"{func}_{col}", {func}(\'{table}\'[{col}])'
            )

    dax = "EVALUATE\nSUMMARIZECOLUMNS(\n"

    dax += ",\n".join(columns)

    if measures:
        dax += ",\n" + ",\n".join(measures)

    dax += "\n)"

    return dax


############################################
# 4. מציאת פורט Power BI
############################################

def find_powerbi_port():

    base = os.path.expandvars(
        r"C:\Users\user\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"
    )

    workspaces = [
        os.path.join(base, d)
        for d in os.listdir(base)
        if d.startswith("AnalysisServicesWorkspace")
    ]

    if not workspaces:
        raise Exception("Power BI workspace not found")

    latest = max(workspaces, key=os.path.getmtime)

    port_file = os.path.join(latest, "Data\msmdsrv.port.txt")
    with open(port_file, "rb") as f:
        raw = f.read()

    port = re.sub(rb"\D", b"", raw).decode()
    if not port:
        raise Exception("Failed to detect Power BI port")

    return port


############################################
# 5. הרצת DAX
############################################

def find_model_database(port):

    conn_str = f"Provider=MSOLAP;Data Source=localhost:{port}"

    with Pyadomd(conn_str) as conn:
        with conn.cursor().execute("SELECT * FROM $SYSTEM.DBSCHEMA_CATALOGS") as cur:

            rows = cur.fetchall()

    if not rows:
        raise Exception("No databases found in SSAS instance")

    db_name = rows[0][0]

    return db_name


def run_dax(query):

    port = find_powerbi_port()

    database = find_model_database(port)

    conn_str = f"Provider=MSOLAP;Data Source=localhost:{port};Catalog={database}"

    with Pyadomd(conn_str) as conn:
        with conn.cursor().execute(query) as cur:

            cols = [c.name for c in cur.description]
            rows = cur.fetchall()

    return pd.DataFrame(rows, columns=cols)


############################################
# 6. workflow ראשי
############################################

def extract_visual(pbip_report_path, visual_title):

    visual_path = find_visual_by_title(pbip_report_path, visual_title)

    fields = extract_fields_from_visual(visual_path)

    fields = clean_fields(fields)

    dax = build_dax_query(fields)

    print("Running query:\n", dax)

    df = run_dax(dax)

    return df


############################################
# שימוש
############################################

def get_data(chartId: str, filters: dict) -> pd.DataFrame:
    PBIP_REPORT_PATH = r"try.Report/definition/pages"
    df = extract_visual(PBIP_REPORT_PATH, title)

    print(df.head())
    return df


get_data("Quantity sold by product")

