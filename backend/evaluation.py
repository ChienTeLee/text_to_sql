import os
import json
import sqlite3
from tqdm import tqdm
from pathlib import Path
from rag import create_document_store, create_rag_pipeline, run_rag_pipeline


def main():
    # set openai key
    os.environ["OPENAI_API_KEY"] = "your_openai_api"

    # create document
    document_file_lst = list(Path("./documents").glob("*.txt"))
    document_store = create_document_store(document_file_lst)
    rag_pipeline = create_rag_pipeline(document_store)
    rag_pipeline.warm_up()

    # prepare dev dataset
    with open("./dataset/spider/dev.json", 'r') as f:
        dev_data_lst = json.load(f)
    # dev_data_lst = dev_data_lst[:100]

    result_dict = {
        "total_num": 0,
        "correct_retrieve_num": 0,
        "correct_generate_num": 0,
    }

    for dev_data in tqdm(dev_data_lst):
        result_dict["total_num"] += 1
        
        # llm db_id, query
        result, retrieved_db_lst = run_rag_pipeline(rag_pipeline, dev_data["question"])
        query1 = result["query"]

        # dataset db_id, query
        real_db_id = dev_data["db_id"]
        query2 = dev_data["query"]

        if real_db_id in retrieved_db_lst:
            result_dict["correct_retrieve_num"] += 1

            # connect db
            sql_db = Path("./dataset/spider/database").joinpath(real_db_id).joinpath(f"{real_db_id}.sqlite")
            con = sqlite3.connect(sql_db)
            cur = con.cursor()

            # check query result
            try:
                cur.execute(query1)
                result1 = cur.fetchall()
            except:
                result1 = "error1"

            try:
                cur.execute(query2)
                result2 = cur.fetchall()
            except:
                result2 = "error2"

            if result1 == result2:
                result_dict["correct_generate_num"] += 1
        
        if result_dict["total_num"] % 10 == 0:
            print(result_dict)

    with open("eval_result.json", 'w') as f:
        json.dump(result_dict, f)


if __name__ == "__main__":
    main()