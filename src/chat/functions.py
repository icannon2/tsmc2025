from ..datasource import SQLRunner
from .state import State


class FunctionCallingBase:
    sql_runner: SQLRunner

    def __init__(self, sql_runner: SQLRunner):
        self.sql_runner = sql_runner

    def duckdb_stmt(self, stmt: str) -> str:
        """
        Run a **single** SQL statement on the DuckDB instance

        Please note that this function is safe to use, as it will not allow any SQL statements that modify the database.

        :param stmt: The SQL statement to run
        :return: The result of the SQL statement

        Example:
        SELECT * FROM orders MATCH_RECOGNIZE(
        PARTITION BY custkey
        ORDER BY orderdate
        MEASURES
                A.totalprice AS starting_price,
                LAST(B.totalprice) AS bottom_price,
                LAST(U.totalprice) AS top_price
        ONE ROW PER MATCH
        AFTER MATCH SKIP PAST LAST ROW
        PATTERN (A B+ C+ D+)
        SUBSET U = (C, D)
        DEFINE
                B AS totalprice < PREV(totalprice),
                C AS totalprice > PREV(totalprice) AND totalprice <= A.totalprice,
                D AS totalprice > PREV(totalprice)
        );
        # the pattern describes a V-shape over the totalprice column. A match is found whenever orders made by a customer first decrease in price, and then increase past the starting point
        """

        result = self.sql_runner.execute_stmt(stmt)
        return f"{result}"
