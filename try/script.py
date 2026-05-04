import json
import pandas as pd
import sys
import os

dll_path = r"C:\Program Files\Microsoft.NET\ADOMD.NET\160"

sys.path.append(dll_path)
os.environ["PATH"] = dll_path + ";" + os.environ["PATH"]
from pyadomd import Pyadomd


#step 1: read visuals

PBIP_REPORT_PATH = "try.Report/definition/pages"

def find_visuals(report_path):
    visuals = []

    for root, dirs, files in os.walk(report_path):
        for file in files:
            if file == "visual.json":
                visuals.append(os.path.join(root, file))

    return visuals


#step 2: extract fields

def extract_fields(visual_file):

    with open(visual_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    projections = []

    query_state = data["visual"]["query"]["queryState"]

    for section in query_state.values():

        if "projections" not in section:
            continue

        for proj in section["projections"]:

            field = proj["field"]

            if "Column" in field:
                table = field["Column"]["Expression"]["SourceRef"]["Entity"]
                column = field["Column"]["Property"]
                projections.append(("column", table, column))

            if "Measure" in field:
                table = field["Measure"]["Expression"]["SourceRef"]["Entity"]
                measure = field["Measure"]["Property"]
                projections.append(("measure", table, measure))

    return projections


#step 3: build dax query

def build_dax_query(fields):

    columns = []
    measures = []

    for ftype, table, name in fields:

        if ftype == "column":
            columns.append(f"'{table}'[{name}]")

        if ftype == "measure":
            measures.append(f'"{name}", [{name}]')

    dax = "EVALUATE\nSUMMARIZECOLUMNS(\n"

    dax += ",\n".join(columns)

    if measures:
        dax += ",\n" + ",\n".join(measures)

    dax += "\n)"

    return dax


#step 4: run query


conn_str = "Provider=MSOLAP;Data Source=localhost:53211;Catalog=Model"

def run_dax(query):

    with Pyadomd(conn_str) as conn:
        with conn.cursor().execute(query) as cur:

            columns = [c.name for c in cur.description]
            rows = cur.fetchall()

    return pd.DataFrame(rows, columns=columns)


#step 5: print results

visuals = find_visuals("try.Report/definition/pages")

for v in visuals:

    fields = extract_fields(v)

    dax = build_dax_query(fields)

    print("Running query:\n", dax)

    df = run_dax(dax)

    print(df.head())