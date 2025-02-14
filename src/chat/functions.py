from abc import ABC
import json
from ..datasource import SQLRunner
from openai.types.chat import ChatCompletionToolParam


class FunctionCallingImpl(ABC):
    spec: ChatCompletionToolParam

    async def process(self, user_prompt: str) -> str:
        pass


class CatalogFunctionCalling(FunctionCallingImpl):
    spec = {
        "type": "function",
        "function": {
            "name": "sql_catalog",
            "description": "Please provide a catalog of the available data tables.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "name of SQL table",
                    },
                },
                "required": ["table"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
    sql_runner: SQLRunner

    def __init__(self, sql_runner: SQLRunner):
        self.sql_runner = sql_runner
        self.spec["function"]["description"] = f"""
List all columns on a SQL table.

available tables: {self.sql_runner.get_tables()}
"""

    async def process(self, user_prompt: str) -> str:
        req = json.loads(user_prompt)
        result = self.sql_runner.get_catalog(req["table"])
        return f"{result}"


class SQLFunctionCalling(FunctionCallingImpl):
    spec = {
        "type": "function",
        "function": {
            "name": "sql_stmt",
            "description": "Please provide a SQL statement to fetch financial data of tech company from the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL statement to run",
                    },
                },
                "required": ["sql"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
    sql_runner: SQLRunner

    def __init__(self, sql_runner: SQLRunner):
        self.sql_runner = sql_runner
        self.spec["function"]["description"] = """
Run a **single** SQL statement tp fetch data from the database.

:param stmt: The SQL statement to run
:return: The result of the SQL statement

Example:
SELECT "Operating Income" FROM FIN_Data_raw WHERE "CompanyName" = 'Apple';
# This will fetch the operating income data of Apple Inc.
SELECT content FROM TRANSCRIPT_Data
JOIN Fiscal_Data
    ON TRANSCRIPT_Data."CompanyName" = Fiscal_Data."CompanyName" AND TRANSCRIPT_Data."CALENDAR_YEAR" = Fiscal_Data."CALENDAR_YEAR" AND TRANSCRIPT_Data."CALENDAR_QTR" = Fiscal_Data."CALENDAR_QTR'
WHERE "CALENDAR_YEAR" = 2021 AND "CALENDAR_QTR" = 'Q1" AND "CompanyName" = 'Apple';
# This will fetch the transcription of Q1 2021(fiscal)'s earning call from apple.
"""

    async def process(self, user_prompt: str) -> str:
        req = json.loads(user_prompt)
        print("running SQL: ", req["sql"])
        result = self.sql_runner.execute_stmt(req["sql"])
        print("result: ", result)
        return f"{result}"
