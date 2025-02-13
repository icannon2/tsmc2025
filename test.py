from src.datasource import SQLRunner, View

if __name__ == "__main__":
    views = [
        View("FIN_Data", "SELECT * FROM FIN_Data_raw"),
        View("TRANSCRIPT_Data", "SELECT * FROM TRANSCRIPT_Data_raw"),
        View("Transcript_File", "SELECT * FROM Transcript_File_raw"),
    ]
    runner = SQLRunner("data/datasource.duckdb", views)
    print(runner.execute_stmt("SELECT * FROM pg_catalog.pg_tables;"))
