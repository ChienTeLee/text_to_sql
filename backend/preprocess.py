import json
from pathlib import Path


def create_document(json_path, document_dir):
    with open(json_path, 'r') as f:
        dev_data = json.load(f)

    db_id_lst = {x["db_id"] for x in dev_data}

    with open("./dataset/spider/tables.json", 'r') as f:
        table_data = json.load(f)
    table_data = [x for x in table_data if x["db_id"] in db_id_lst]

    document_folder = Path(document_dir)
    document_folder.mkdir(parents=True, exist_ok=True)

    for table in table_data:
        table_names = table["table_names_original"]
        column_names = table["column_names_original"]
        db_id = table["db_id"]
        filepath = document_folder.joinpath(f"{db_id}.txt")

        for x in column_names:
            if x[0]!= -1:
                table_name = table_names[x[0]]
                column_name = x[1]
                d = {
                    "db_id": db_id,
                    "table_name": table_name,
                    "column_name": column_name,
                }
                with open(filepath, "a+") as f:
                    json.dump(d, f)
                    f.write('\n')


def main():
    json_path = "./dataset/spider/dev.json"
    document_dir = "./documents"
    create_document(json_path, document_dir)


if __name__ == "__main__":
    main()