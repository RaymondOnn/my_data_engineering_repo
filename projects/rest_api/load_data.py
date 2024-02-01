import os
import duckdb


def get_inputs(dir_path):
    tables = {}
    with os.scandir(dir_path) as file_dir:
        for file in file_dir:
            if file.path.endswith('.csv'):
                table_name = os.path.splitext(file.name)[0]
                tables[table_name] = file.path
    return tables


def create_table(conn, tbl_name, file_path):
    drop_query = f"DROP TABLE IF EXISTS {tbl_name}"
    create_query = f"CREATE TABLE {tbl_name} AS SELECT * FROM read_csv_auto('{file_path}', HEADER=TRUE)"
    for q in [drop_query, create_query]:
        print(f'Executing: {q}')
        conn.sql(q)
    return True


def main():
    DB_FILE = './database/database.db'
    DATA_DIR = './data'

    conn = duckdb.connect(DB_FILE)
    tables = get_inputs(DATA_DIR)
    for k, v in tables.items():
        create_table(conn, k, v)
        
        
if __name__ == '__main__':
    main()
