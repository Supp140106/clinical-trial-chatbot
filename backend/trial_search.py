import sqlite3
import os
from schema import SearchFilters, MapboxOutput, MapboxTrial

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/clinical_trials_demo.db")

def search_trials(filters: SearchFilters) -> MapboxOutput:
    """
    Searches the SQLite database using the extracted filters.
    Returns a MapboxOutput object containing the list of matching trials.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM clinical_trials WHERE 1=1"
    params = []

    if filters.cancer_type:
        query += " AND cancer_type LIKE ?"
        params.append(f"%{filters.cancer_type}%")

    if filters.trial_phase:
        query += " AND trial_phase LIKE ?"
        params.append(f"%{filters.trial_phase}%")

    if filters.recruitment_status:
        query += " AND recruitment_status LIKE ?"
        params.append(f"%{filters.recruitment_status}%")

    if filters.location:
        # Check against city or province
        query += " AND (city LIKE ? OR province LIKE ?)"
        params.extend([f"%{filters.location}%", f"%{filters.location}%"])

    # We limit to 10 for mapping purposes in this demo (or all)
    query += " LIMIT 20"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    mapbox_trials = []
    for row in rows:
        mapbox_trials.append(MapboxTrial(
            trial_code=row["trial_code"],
            trial_title=row["trial_title"],
            hospital=row["hospital_name"],
            latitude=row["latitude"],
            longitude=row["longitude"]
        ))

    return MapboxOutput(trials=mapbox_trials)
