import logging

from repositories.base_repository import BaseRepository


class LocalSchemaRepository(BaseRepository):

    def create_tables_if_not_exists(self):
        existing_tables = [
            row.table_name for row in self.connection.cursor().tables(tableType='TABLE')
        ]

        create_tables_queries = {
            "tblInventory": """
                CREATE TABLE tblInventory (
                    StoreNo TEXT(50) PRIMARY KEY,
                    StoreName TEXT(50),
                    JobDateTime DATETIME,
                    Address TEXT(255)
                )
            """,
            "tblEmps": """
                CREATE TABLE tblEmps (
                    EmpNo TEXT(50),
                    StoreNo TEXT(50),
                    EmpName TEXT(255),
                    TotalTags INTEGER,
                    TotalQty INTEGER,
                    TotalEXTPRICE DOUBLE,
                    DiscrepancyDollars DOUBLE,
                    DiscrepancyTags INTEGER,
                    Hours DOUBLE
                )
            """,
            "tblZones": """
                CREATE TABLE tblZones (
                    ZoneID TEXT(50),
                    StoreNo TEXT(50),
                    ZoneDesc TEXT(255),
                    TotalTags INTEGER,
                    TotalQty INTEGER,
                    TotalEXTPRICE DOUBLE,
                    DiscrepancyDollars DOUBLE,
                    DiscrepancyTags INTEGER
                )
            """,
            "tblDiscrepancies": """
                CREATE TABLE tblDiscrepancies (
                    StoreNo TEXT(50),
                    EmpNo TEXT(50),
                    ZoneID TEXT(50),
                    TagNo TEXT(50),
                    UPC TEXT(50),
                    EXTPRICE DOUBLE,
                    OrigQty INTEGER,
                    NewQty INTEGER,
                    DiscrepancyDollars DOUBLE
                )
            """
        }

        for table_name, create_sql in create_tables_queries.items():
            if table_name not in existing_tables:
                logging.info(f"Creating table: {table_name}")
                self._execute(create_sql)