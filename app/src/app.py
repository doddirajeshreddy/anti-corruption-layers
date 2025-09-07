from flask import Flask, jsonify, request
import os
import psycopg2
import yaml

app = Flask(__name__)

# Load configuration from YAML file (assumed to be mounted or available as config.yaml)
with open("config.yaml", "r") as f:
    config_data = yaml.safe_load(f)

# The YAML is expected to have a top-level key "mappings" with a list of mapping entries.
mappings = config_data.get("mappings", [])

# Database connection details
db_config = {
    'user': os.getenv("POSTGRES_USER", "postgres"),
    'host': os.getenv("POSTGRES_HOST", "postgres-service"),
    'database': os.getenv("POSTGRES_DB", "mydb"),
    'password': os.getenv("POSTGRES_PASSWORD", "password"),
    'port': int(os.getenv("POSTGRES_PORT", 5432)),
}

@app.route("/<path:path>", methods=["GET"])
def index(path):
    # Prepend a slash to match our mapping config (e.g., "myapi" becomes "/myapi")
    endpoint = "/" + path

    # Look up the mapping configuration for this endpoint.
    mapping_entry = None
    for m in mappings:
        if m.get("api_endpoint") == endpoint:
            mapping_entry = m
            break

    if mapping_entry is None:
        return jsonify({"error": f"Endpoint '{endpoint}' not configured."}), 404

    query = mapping_entry.get("query")
    if not query:
        return jsonify({"error": "No query defined for this endpoint."}), 500

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        # Get column names from the cursor (each column’s name is in cur.description)
        columns = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()

        # Transform the rows into a list of dicts using the configured column mapping.
        transformed = transform_data(rows, columns, mapping_entry.get("columns", {}))
        return jsonify(transformed)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def transform_data(rows, columns, col_mapping):
    """
    Transform each row (a tuple) into a dictionary using the provided column mapping.
    Only columns listed in the mapping will be returned, and the keys will be renamed.
    """
    result = []
    # Convert each row tuple to a dict mapping original column names to values.
    for row in rows:
        row_data = dict(zip(columns, row))
        transformed_row = {}
        # For every mapping from database column name to desired API response field name:
        for db_col, api_field in col_mapping.items():
            # Only include the column if it exists in the row data.
            if db_col in row_data:
                transformed_row[api_field] = row_data[db_col]
        result.append(transformed_row)
    return result

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
