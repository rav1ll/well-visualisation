import json
import os
import psycopg2

def json_reader(input_path):
    conn = psycopg2.connect(
        host="localhost",
        database="pipe_data",
        user="postgres",
        password="1234"
    )

    cursor = conn.cursor()

    with open(input_path, 'r', encoding='UTF-8') as f:
        data = json.loads(f.read())

        pipe_data = data['data']


    cursor.execute("SELECT * FROM pipes_data")

    # for item in pipe_data:
    #     values = tuple(item.values())
    #     placeholders = ', '.join(['%s'] * len(values))
    #     query = "INSERT INTO pipes_data (id, tipn, npo_idn, tipk, npo_idk, uch_id, kod_ngdu, cex, brig, cnam, dubl, pipe_dat, nazn, qg, qg_vrez, p_fak, p_fak_vrez, obw, agent, uch_dat, int1, int2, sost_t, d_tr, t_st, glub, fl_diag, vrez, cnt, ckt, tip) VALUES (%s)" % placeholders
    #
    #     cursor.execute(query, values)



    # cursor.execute("INSERT INTO your_table (id, tipn, npo_idn, tipk, npo_idk, uch_id, kod_ngdu, cex, brig, cnam, dubl, pipe_dat, nazn, qg, qg_vrez, p_fak, p_fak_vrez, obw, agent, uch_dat, int1, int2, sost_t, d_tr, t_st, glub, fl_diag, vrez, cnt, ckt, tip)"
    #                "VALUES ")
    conn.commit()
    results = cursor.fetchall()
    print(results)
    conn.close()


input_path = 'input_data/pipe_data.json'
if __name__ == "__main__":
    json_reader(input_path)
