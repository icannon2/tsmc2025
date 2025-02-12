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

    def __init__(self, path, views: list[View] = []):
        self.duckdb = connect(path, read_only=True)
        self.views = views
        for view in views:
            self.duckdb.execute(view.query)

    """
    Check if the query is valid
    """

    def check_query(self, stmt: str):
        # duckdb is compatible with postgres
        query = parse_one(stmt, dialect="postgres")
        for table in query.find_all(exp.Table):
            if next(filter(lambda x: x.name == table.name, self.views), None) is None:
                raise Exception(f"Table {table.name} does not exist")
        for view in query.find_all(exp.Create):
            if next(filter(lambda x: x.name == view.name, self.views), None) is None:
                raise Exception(
                    f"Database is read-only, cannot create view {view.name}"
                )

    def execute_stmt(self, query) -> ExecutionResult:
        try:
            self.check_query(query)
            result = self.duckdb.sql(query)
        except Exception as e:
            return ExecutionResult(error_message=str(e))

        return ExecutionResult(result=result)
