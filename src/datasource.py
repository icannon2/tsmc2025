from sqlglot import parse_one, exp

from discord import Role

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


def roles_to_views(roles: list[Role]) -> list[View]:
    country = {
        1339499087489273868: "USA",
        1339499042278735872: "China",
        1339498984930017342: "Switzerland",
        1339498929901015100: "Taiwan",
        1339498806856646668: "South Korea",
    }
    roles = list(filter(lambda x: x["id"] in country, roles))
    if roles is None:
        return []
    country_str = f"'{"','".join(map(lambda x: country[x['id']], roles))}'"

    return [
        View(
            "FIN_data",
            f"""
             SELECT * FROM FIN_data_raw
             WHERE Country IN ({country_str})
             """,
        ),
        View(
            "TRANSCRIPT_Data",
            """
             SELECT * FROM TRANSCRIPT_Data_raw
            
             """,
        ),
        View(
            "FIN_Data_Derived",
            f"""
             SELECT * FROM FIN_Data_Derived_raw
             WHERE Country IN ({country_str})
             """,
        ),
        View("Exchange_Rate", "SELECT * FROM Exchange_Rate_raw"),
        View("Fiscal_Data", "SELECT * FROM Fiscal_Data_raw"),
    ]


class SQLRunner:
    duckdb: DuckDBPyConnection
    views: list[View]
    protected_tables: list[str] = []

    def __init__(self, path, roles: list[Role] = []):
        self.duckdb = connect(path, read_only=True)

        for protected_table in self.duckdb.sql("SHOW TABLES;").fetchall():
            self.protected_tables.append(protected_table[0])

        self.views = roles_to_views(roles)
        for view in self.views:
            self.duckdb.execute(view.query)
        self.duckdb.execute("SET enable_external_access = false;")

    def get_tables(self) -> list[str]:
        return list(map(lambda x: x.name, self.views))

    def get_catalog(self, table: str) -> str:
        tables = self.get_tables()
        if table not in tables:
            return f"Error: Table with name {table} does not exist!"

        result = []

        for row in self.duckdb.sql(f"""
            SELECT
                column_name, data_type
            FROM
                information_schema.columns
            WHERE
                table_name = '{table}';
            """).fetchall():
            result.append(f'"{row[0]}"({row[1]})')

        return ", ".join(result)

    def check_query(self, stmt: str):
        """
        Check if the query is valid
        """
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
        if next(query.find_all(exp.Copy), None) is not None:
            raise Exception("Error: Database lockdown: DML is not allowed!")

    def add_view(self, view: View):
        self.duckdb.execute(view.query)
        self.views.append(view)

    def execute_stmt(self, query) -> ExecutionResult:
        try:
            self.check_query(query)
            result = self.duckdb.sql(query)
        except Exception as e:
            return ExecutionResult(error_message=str(e))

        return ExecutionResult(result=result)
