from ..datasource import SQLRunner

from google.genai.client import Client


async def singleShotCompletion(
    genai, systemPrompt: str, userPrompt: str, tools: list = []
):
    """
    Generates a single-shot completion for the given user prompt.

    Args:
        systemPrompt (str): The system prompt
        userPrompt (str): The user prompt
        tools (list): The list of tools to use

    Returns:
        str: The completion for the given user prompt
    """

    # TODO: this doesn't work, need to fix

    if genai is None:
        raise Exception("This function requires a GenAI client to be initialized")

    result = genai.generate_content(
        model="gemini-2.0-flash",
        systemPrompt=systemPrompt,
        userPrompt=userPrompt,
        tools=tools,
    )

    return f"{result}"


class FunctionCalling:
    sql_runner: SQLRunner
    genai: Client | None

    def __init__(self, sql_runner: SQLRunner, genai: Client | None = None):
        self.sql_runner = sql_runner
        self.genai = genai

        self.duckdb_stmt.__func__.__doc__ = f"""
            Run a **single** SQL statement tp fetch financial data of tech company from the database.

            Available Tables: {self.sql_runner.get_catalog()}

            Please note that this function is safe to use, as it will not allow any SQL statements that modify the database.

            :param stmt: The SQL statement to run
            :return: The result of the SQL statement

            Example:
            SELECT "Operating Income" FROM FIN_Data_raw WHERE "CompanyName" = 'Apple';
            # This will fetch the operating income data of Apple Inc.
            SELECT "Return_on_Assets" FROM FIN_Data_raw WHERE "CompanyName" = 'Baidu';
            # This will fetch the return on assets data of Baidu Inc.
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

    def duckdb_stmt(self, stmt: str) -> str:
        result = self.sql_runner.execute_stmt(stmt)
        return f"{result}"

    async def get_transcription(self, year: int, qtr: int) -> str:
        """
        Get the transcription of company's institutional investors conference call

        :param year: The year of the conference call
        :param qtr: The quarter of the conference call
        :return: The transcription of the conference call
        """

        result = f"{
            self.sql_runner.execute_stmt(
                f"SELECT * FROM TRANSCRIPT_Data WHERE year = {year} AND qtr = 'Q{qtr}'"
            )
        }"

        if self.genai is None:
            return result

        return await singleShotCompletion(
            self.genai,
            """
            Please transcribe the conference call for the given year and quarter
            """,
            result,
        )

    # def get_fin_data(self, metrics: str, company) -> str:
    #     """
    #     Get the financial data of a country

    #     :param stmt: The SQL statement to transcribe
    #     :return: The transcription of the SQL statement
    #     """

    #     result = self.sql_runner.execute_stmt(
    #         f"SELECT * FROM FIN_data WHERE \"CompanyName\" = '{company}'"
    #     )

    #     return f"{result}"

    # def research_planner(self, stmt: str) -> str:
    #     """
    #     Generates the search queries prompt for the given question.
    #     Args:
    #         question (str): The question to generate the search queries prompt for
    #         parent_query (str): The main question (only relevant for detailed reports)
    #         report_type (str): The report type
    #         max_iterations (int): The maximum number of search queries to generate
    #         context (str): Context for better understanding of the task with realtime web information

    #     Returns: str: The search queries prompt for the given question
    #     """

    #     if self.genai is None:
    #         raise Exception("This function requires a GenAI client to be initialized")

    #     result = self.sql_runner.execute_stmt(f"EXPLAIN {stmt}")

    #     return f"{result}"
