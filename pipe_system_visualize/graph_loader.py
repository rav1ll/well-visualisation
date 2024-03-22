import json
import os

import networkx as nx
from matplotlib import pyplot as plt


def main():
    with open(os.path.join('input_data', 'pipe_data.json'), 'r', encoding='UTF-8') as file:
        pipe_data = json.load(file)['data']

    pipes_dict = {}
    for item in pipe_data:
        obj_id = item['id']
        obj_idk = item['npo_idk']
        obj_idn = item['npo_idn']
        if obj_id not in pipes_dict and item["sost_t"] ==  58 and (item['tipn'] == 10 or item['tipk'] == 10):
            pipes_dict[obj_id] = (obj_idn, obj_idk)



    G = nx.Graph()


    for object in pipes_dict:
        G.add_edge(pipes_dict[object][0], pipes_dict[object][1])

    plt.figure(figsize=(20, 20))
    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=10, node_color='lightblue', font_weight='bold', font_size=10)

    plt.show()

if __name__ == "__main__":
    main()
