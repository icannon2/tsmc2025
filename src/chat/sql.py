import duckdb
from chat import FunctionCalling, State


class DuckDB(FunctionCalling):
    def __init__(self, state: State):
        self.name = "DuckDB"
        self.description = "A SQL database that can be accessed from the chatroom."
        self.parameters = None
        self.state = state
        self.db = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.db = duckdb.connect(':memory:')
        self.cursor = self.db.cursor()
        
        # copy data to memory table if it's csv
        # INSERT INTO test SELECT * FROM 'test.csv';

        # google cloud stroage example
        # CREATE SECRET (
        #     TYPE GCS,
        #     KEY_ID 'AKIAIOSFODNN7EXAMPLE',
        #     SECRET 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        # );
        # INSERT INTO test SELECT * FROM 'gs://⟨gcs_bucket⟩/⟨file.csv⟩';

        # example usage
        # self.cursor.execute("CREATE TABLE test (a INTEGER, b VARCHAR);")
        # self.cursor.execute("INSERT INTO test VALUES (1, 'foo');")
        # self.cursor.execute("INSERT INTO test VALUES (2, 'bar');")

    def process(self, request: str):
        self.cursor.execute(request)
        return self.cursor.fetchall()
