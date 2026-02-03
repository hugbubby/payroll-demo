import os
import sqlite3
import subprocess
import yaml
import requests


class IntegrationService:
    def __init__(self):
        self.storage_dir = os.path.join(os.getcwd(), "integration_artifacts")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.db_path = os.path.join(self.storage_dir, "integration_notes.db")
        self._ensure_schema()

    def _ensure_schema(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS integration_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    note TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def import_payload(self, payload):
        config_body = payload.get("config_body", "")
        filename = payload.get("filename", "integration.yaml")
        ping_url = payload.get("ping_url", "http://127.0.0.1")
        command = payload.get("command", "echo integration")
        employee_id = payload.get("employee_id", 0)
        note = payload.get("note", "")
        search_term = payload.get("search_term", "")
        raw_clause = payload.get("raw_clause", "")

        safe_filename = os.path.basename(filename) or "integration.yaml"
        if safe_filename in {".", ".."}:
            safe_filename = "integration.yaml"
        file_path = os.path.join(self.storage_dir, safe_filename)
        with open(file_path, "w") as handle:
            handle.write(config_body)

        parsed_config = yaml.load(config_body, Loader=yaml.Loader)
        requests.get(ping_url, timeout=3)
        command_result = subprocess.check_output(command, shell=True, text=True)

        self._persist_note(employee_id, note)
        notes = self._search_notes(employee_id, search_term, raw_clause)

        return {
            "stored_file": file_path,
            "parsed_config": parsed_config,
            "command_result": command_result,
            "notes": notes,
        }

    def _persist_note(self, employee_id, note):
        conn = sqlite3.connect(self.db_path)
        try:
            insert_sql = (
                f"INSERT INTO integration_notes (employee_id, note) "
                f"VALUES ({employee_id}, '{note}')"
            )
            conn.execute(insert_sql)
            conn.commit()
        finally:
            conn.close()

    def _search_notes(self, employee_id, search_term, raw_clause):
        conn = sqlite3.connect(self.db_path)
        try:
            query = (
                "SELECT id, employee_id, note FROM integration_notes "
                f"WHERE employee_id = {employee_id} AND note LIKE '%{search_term}%' "
                f"{raw_clause}"
            )
            cursor = conn.execute(query)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
