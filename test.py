from src.datasource import SQLRunner

if __name__ == "__main__":
    roles = [
        {
            "id": 1339499087489273868,
        },
    ]
    runner = SQLRunner("data/datasource.duckdb", roles)

    print(
        runner.execute_stmt("SELECT * FROM pg_catalog.pg_tables;")
    )  # This will not work
    print(runner.execute_stmt("SELECT * FROM FIN_data;"))  # This will work
    print(runner.get_catalog())
