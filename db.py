import sqlite3
import json
from datetime import datetime
import logging

class DatabaseManager:
    def __init__(self, db_path="document_extraction.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with the documents table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ocr_data JSON,
                    extracted_data JSON
                )
            ''')
            conn.commit()
            logging.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
        finally:
            if conn:
                conn.close()

    def insert_document(self, filename, ocr_data, extracted_data):
        """Insert a new document record."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents (filename, ocr_data, extracted_data)
                VALUES (?, ?, ?)
            ''', (filename, json.dumps(ocr_data), json.dumps(extracted_data)))
            doc_id = cursor.lastrowid
            conn.commit()
            return doc_id
        except Exception as e:
            logging.error(f"Failed to insert document: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_document(self, doc_id):
        """Retrieve a document by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "filename": row[1],
                    "upload_timestamp": row[2],
                    "ocr_data": json.loads(row[3]) if row[3] else None,
                    "extracted_data": json.loads(row[4]) if row[4] else None
                }
            return None
        except Exception as e:
            logging.error(f"Failed to retrieve document {doc_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def list_documents(self):
        """Retrieve all documents."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, filename, upload_timestamp FROM documents ORDER BY upload_timestamp DESC')
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                documents.append({
                    "id": row[0],
                    "filename": row[1],
                    "upload_timestamp": row[2]
                })
            return documents
        except Exception as e:
            logging.error(f"Failed to list documents: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def delete_document(self, doc_id):
        """Delete a document by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
            rows_deleted = cursor.rowcount
            
            # Check if table is empty, if so, reset ID counter
            cursor.execute('SELECT COUNT(*) FROM documents')
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='documents'")
                
            conn.commit()
            return rows_deleted > 0
        except Exception as e:
            logging.error(f"Failed to delete document {doc_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
