"""Create and seed the planetarium_facts table using one SQL statement per execute call."""

from __future__ import annotations

import json

from planetarium import DATA_PATH, DATABASE_FACT_KEYS, ZetarisClient

CREATE_TABLE_SQL = """CREATE TABLE planetarium_facts (
    planet_name VARCHAR(32) PRIMARY KEY,
    position VARCHAR(80),
    classification VARCHAR(80),
    diameter_km VARCHAR(80),
    mean_solar_distance_au VARCHAR(80),
    orbital_period_earth_days VARCHAR(80),
    rotation_period VARCHAR(120),
    axial_tilt VARCHAR(160),
    reference_gravity VARCHAR(120),
    known_moons VARCHAR(40),
    rings VARCHAR(600),
    atmosphere VARCHAR(1000),
    signature_fact VARCHAR(1500),
    source_url VARCHAR(500)
)"""


def seed() -> None:
    client = ZetarisClient()
    if not client.configured:
        raise RuntimeError("Set ZETARIS_URL, ZETARIS_USER, ZETARIS_PASSWORD, and ZETARIS_JAR first.")

    with DATA_PATH.open(encoding="utf-8") as catalog_file:
        planets = json.load(catalog_file)["planets"]

    connection = client.connect()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(CREATE_TABLE_SQL)
            connection.commit()
        except Exception:
            connection.rollback()
            cursor.execute("SELECT planet_name FROM planetarium_facts WHERE planet_name = ?", ("Mercury",))
            cursor.fetchone()

        columns = ("planet_name",) + DATABASE_FACT_KEYS + ("source_url",)
        placeholders = ", ".join("?" for _ in columns)
        insert_sql = f"INSERT INTO planetarium_facts ({', '.join(columns)}) VALUES ({placeholders})"
        for planet in planets:
            cursor.execute("SELECT planet_name FROM planetarium_facts WHERE planet_name = ?", (planet["name"],))
            if cursor.fetchone() is not None:
                continue
            values = [planet["name"]] + [
                str(planet["facts"][key]) for key in DATABASE_FACT_KEYS
            ] + [planet["source_url"]]
            cursor.execute(insert_sql, tuple(values))
        connection.commit()
        cursor.close()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    print(f"Seeded missing records for {len(planets)} planets in planetarium_facts.")


if __name__ == "__main__":
    seed()