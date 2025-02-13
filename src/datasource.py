from sqlglot import parse_one, exp

from duckdb import DuckDBPyConnection, connect, DuckDBPyRelation


class View:
    name = None
    query: str

    def __init__(self, view_name, query, materialize=False):
        self.name = view_name
        self.query = f"CREATE TEMP {'MATERIALIZED VIEW' if materialize else 'VIEW'} {view_name} AS {query}"


class ExecutionResult:
    error_message: str | None
    result: DuckDBPyRelation

    def __init__(self, **kwargs):
        self.error_message = kwargs.get("error_message")
        self.result = kwargs.get("result")

    def map_row(self, row):
        obj = {}
        for value, key in zip(row, self.result.columns):
            obj[key] = value
        return obj

    def __str__(self):
        if self.error_message is not None:
            return f"Error: {self.error_message}"

        rows = self.result.fetchall()
        return f"{list(map(self.map_row, rows))}"


class SQLRunner:
    duckdb: DuckDBPyConnection
    views: list[View]
    protected_tables: list[str] = []

    def __init__(self, path, views: list[View] = []):
        self.duckdb = connect(path, read_only=True)

        for protected_table in self.duckdb.sql("SHOW TABLES;").fetchall():
            self.protected_tables.append(protected_table[0])

        self.views = views
        for view in views:
            self.duckdb.execute(view.query)
        self.duckdb.execute("SET enable_external_access = false;")

    """
    Check if the query is valid
    """

    def check_query(self, stmt: str):
        query = parse_one(stmt, dialect="postgres")
        for table in query.find_all(exp.Table):
            if table.name in self.protected_tables:
                raise Exception(
                    f"Error: Catalog Error: Table with name {table.name} does not exist!"
                )
            if table.name.startswith("pg_"):
                raise Exception(
                    f"Error: Catalog Error: Table with name {table.name} does not exist!"
                )

        if next(query.find_all(exp.Create), None) is not None:
            raise Exception("Error: Database lockdown: DML and DCL are not allowed!")
        if next(query.find_all(exp.Drop), None) is not None:
            raise Exception("Error: Database lockdown: DDL is not allowed!")
        if next(query.find_all(exp.Alter), None) is not None:
            raise Exception("Error: Database lockdown: DDL is not allowed!")
        if next(query.find_all(exp.Set), None) is not None:
            raise Exception("Error: Database lockdown: DML is not allowed!")
        if next(query.find_all(exp.Show), None) is not None:
            raise Exception("Error: Database lockdown: DML is not allowed!")

    def execute_stmt(self, query) -> ExecutionResult:
        try:
            self.check_query(query)
            result = self.duckdb.sql(query)
        except Exception as e:
            return ExecutionResult(error_message=str(e))

        return ExecutionResult(result=result)
