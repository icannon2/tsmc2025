from abc import ABC
import json
from ..datasource import SQLRunner
from openai.types.chat import ChatCompletionToolParam
from ..datasource import View
import uuid


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
Run a **single** SQL statement to fetch data from the database.

:param stmt: The SQL statement to run
:return: The result of the SQL statement

Example:
SELECT "OperatingIncome" FROM FIN_Data_raw WHERE "CompanyName" = 'Apple';
# This will fetch the operating income data of Apple Inc.
SELECT content FROM TRANSCRIPT_Data
JOIN Fiscal_Data
    ON TRANSCRIPT_Data."CompanyName" = Fiscal_Data."CompanyName" AND TRANSCRIPT_Data."CalenderYear" = Fiscal_Data."CalenderYear" AND TRANSCRIPT_Data."CalendarQuarter" = Fiscal_Data."CalendarQuarter'
WHERE "CalenderYear" = 2021 AND "CalendarQuarter" = 'Q1" AND "CompanyName" = 'Apple';
# This will fetch the transcription of Q1 2021(fiscal)'s earning call from apple.
"""

    async def process(self, user_prompt: str) -> str:
        req = json.loads(user_prompt)
        print("running SQL: ", req["sql"])
        result = self.sql_runner.execute_stmt(req["sql"])
        print("result: ", result)
        return f"{result}"


class IcebergeConntection(FunctionCallingImpl):
    spec = {
        "type": "function",
        "function": {
            "name": "connect_iceberg",
            "description": "Connect to Iceberg datalake with uri.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uri": {
                        "type": "string",
                        "description": "uri of Iceberg datalake",
                    },
                },
                "required": ["uri"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
    sql_runner: SQLRunner

    def __init__(self, sql_runner: SQLRunner):
        self.sql_runner = sql_runner

    async def process(self, user_prompt: str) -> str:
        req = json.loads(user_prompt)
        rand = uuid.uuid4()
        uri = req["uri"]

        try:
            view = View(
                "Iceberg_{uuid}",
                f"SELECT * FROM \iceberg_scan('{uri}',allow_moved_paths = true);",
            )
            self.sql_runner.add_view(view)
        except Exception as e:
            return f"Error: {e}"

        return (
            f"Connected to Iceberg datalake with uri: {uri}, table name: Iceberg_{rand}"
        )
