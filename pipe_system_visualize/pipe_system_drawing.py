import os
import sys
import json
import logging
from collections import defaultdict

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import cm
from pyvis import network as net


class pipeSystemDrawing():

    def __init__(self):
        self.pipe_data = {}

        self.obj_id = -1
        self.pipes = []

        self.node_size = 40
        self.font_size = 14
        self.line_width = 1
        self.font_bold = 'normal'

        self.single_pic = False
        self.draw_wells = False
        self.npok = 0
        self.labels = {}
        self.npoz_ignore_list = []

        self.mk_log()
        self.loadConfig()

        self.npoz = None  # список ТП

    def mk_log(self):
        '''генерация log файла для записи информации о работе модуля'''
        try:
            logging.basicConfig(format=u'%(levelname)-8s : %(message)s', level=logging.INFO,
                                filename=os.path.join('output_data', 'report.txt'), filemode='w')
        except BaseException as e:
            print('Ошибка в генерации log файла: {}'.format(str(e)))

    def loadConfig(self):
        '''загрузка параметров конфигурации'''
        try:
            dc = None
            with open(os.path.join('input_data', 'config.json'), 'r') as fc:
                dc = json.load(fc)
        except BaseException as e:
            err_msg = 'Ошибка при загрузке файла конфигурации:' + str(e)
            print(err_msg)
            logging.error(err_msg)
            raise Exception(err_msg)

        self.obj_id = dc['npo_id']
        self.node_size = dc['node_size']
        self.font_size = dc['font_size']
        self.line_width = dc['line_width']
        self.pipe_code = dc['pipe_code']
        self.optimal_debit = dc['min_debit']
        self.font_color = dc['font_color']
        self.graph_bg_color = dc['graph_bg_color']
        self.node_color = dc['node_color']
        if dc['font_bold']:
            self.font_bold = 'bold'

        self.press_deviation = dc['pressure_deviation']
        self.optimal_pressure = dc['pressure_optimal_value']

        # if self.obj_id == -1:

        self.npoz_ignore_list = []
        npok = dc['npok']
        if npok == 0:
            self.npoz_ignore_list = [1, 7, 92]
        elif npok == 1:
            self.npoz_ignore_list = [1, 92]
        # self.npoz_ignore_list = []

        self.single_pic = False
        single_pic = dc['single_pic']
        if single_pic == 1:
            self.single_pic = True

            self.draw_wells = False
        else:
            self.draw_wells = dc['draw_wells']


    def load_pipe_data(self):
        '''загрузка данных по трубопроводам'''
        try:
            with open(os.path.join('input_data', 'final_pipe_data.json'), 'r', encoding='UTF-8') as fin:
                pipe_data = json.load(fin)['data']

                for val in pipe_data:

                    if val['tipn'] == 92: continue

                    if val['agent'] == 'oil':
                        if val['id'] not in self.pipe_data:
                            self.pipe_data[val['id']] = []
                        self.pipe_data[val['id']].append(val)
        except BaseException as e:
            err_msg = 'Ошибка в загрузке данных:\n{}'.format(e)
            print(err_msg)
            logging.error(err_msg)
            sys.exit()

    def get_all_npo(self):
        '''сбор всех товарных парков'''
        self.npoz = {self.pipe_data[val][0]['npo_idk']: self.pipe_data[val][0]['ckt'] for val in self.pipe_data if
                     self.pipe_data[val][0]['tipn'] == 5 and self.pipe_data[val][0]['tipk'] == 10}

    def get_pipe_with_obj(self, obj_id):
        '''поиск трубы с заданным объектом'''

        pipes_with_obj = []
        if self.obj_id == -1:
            pipes_with_obj = [tube_id for tube_id in self.pipe_data if self.pipe_data[tube_id][0]['npo_idk'] == obj_id
                              and self.pipe_data[tube_id][0]['tipk'] == 10]
        else:
            check = [tube_id for tube_id in self.pipe_data if self.pipe_data[tube_id][0]['npo_idk'] == obj_id]
            if check:
                if self.pipe_data[check[0]][0]['tipk'] != 10:
                    pipes_with_obj = [tube_id for tube_id in self.pipe_data if
                                      self.pipe_data[tube_id][0]['npo_idn'] == obj_id]
                else:
                    pipes_with_obj = [tube_id for tube_id in self.pipe_data if
                                      self.pipe_data[tube_id][0]['npo_idk'] == obj_id]

        return pipes_with_obj

    def assemble_pipe_system(self, tube):
        draw_wells = self.draw_wells
        used_pipes = []
        selected_keys = ["id", "tipn", "tipk", "cnt", "ckt", "pipe_dat", "cnam", "npo_idn", "npo_idk", "agent"]
        '''сбор трубопроводной сети'''
        node_label_by_id = {}
        edge_labelz = {}
        pipe = self.pipe_data[tube]

        found_pipes = [tube]
        found_pipes_idz = [tube]

        iter = 0
        plt.clf()

        G = nx.Graph()
        G.add_edge(self.pipe_data[tube][0]['cnt'], self.pipe_data[tube][0]['ckt'])

        node_label_by_id[self.pipe_data[tube][0]['npo_idn']] = self.pipe_data[tube][0]['cnt']
        node_label_by_id[self.pipe_data[tube][0]['npo_idk']] = self.pipe_data[tube][0]['ckt']

        edge_labelz[(self.pipe_data[tube][0]['cnt'], self.pipe_data[tube][0]['ckt'])] = {
            'id': self.pipe_data[tube][0]['id'],
            'edge': (self.pipe_data[tube][0]['cnt'], self.pipe_data[tube][0]['ckt']),
            'values': {}
        }

        while 1:
            '''сбор труб с учетом нулевых идентификаторов, если сеть обрывается, выводим в лог сообщение'''
            for check_id in found_pipes_idz:
                # check pipe - труба, идущая от ТП до объекта
                check_pipe = self.pipe_data[check_id][0]
                if check_pipe['npo_idn'] == 0:
                    continue
                for key in self.pipe_data:
                    key_pipe = self.pipe_data[key][0]
                    if key_pipe['npo_idk'] == 0:
                        continue
                    if key in found_pipes or key in found_pipes_idz:
                        continue

                    if not draw_wells:
                        if key_pipe['tipn'] == 1:
                            continue

                    '''Обработка врезок'''

                    if (key_pipe['tipk'] == self.pipe_code and (
                            key_pipe['ckt'] == check_pipe['cnam'] or key_pipe['npo_idk'] == check_pipe['id'])) or (
                            key_pipe['tipk'] != self.pipe_code and key_pipe['ckt'] == check_pipe['cnt']):

                        found_pipes.append(key)

                        if key_pipe['tipk'] == self.pipe_code:
                            if check_pipe['tipk'] != self.pipe_code:

                                key1 = 'cnt'

                                key2 = 'cnt'
                                if check_pipe['tipn'] in self.npoz_ignore_list:
                                    # key1 = 'npo_idk'
                                    key1 = 'ckt'

                                    key2 = 'ckt'

                                # G.add_edge(key_pipe['npo_idn'], check_pipe[key1])
                                G.add_edge(key_pipe['cnt'], check_pipe[key1])
                                selected_data = {key: key_pipe[key] for key in selected_keys}
                                used_pipes.append(selected_data)

                                node_label_by_id[key_pipe['npo_idn']] = key_pipe['cnt']
                                node_label_by_id[check_pipe[key1]] = check_pipe[key2]

                                edge_labelz[(key_pipe['cnt'], check_pipe[key1])] = {'id': key_pipe['id'], 'edge': (
                                    key_pipe['cnt'], check_pipe[key1]),
                                                                                    }

                            else:
                                # check_pipe tipk = 122
                                vrez_id = check_pipe['npo_idk']
                                check_pipe_2 = self.pipe_data[vrez_id][0]

                                while check_pipe_2['tipk'] == self.pipe_code:
                                    new_vrez_id = check_pipe_2['npo_idk']
                                    check_pipe_2 = self.pipe_data[new_vrez_id][0]
                                    if check_pipe_2['tipk'] != self.pipe_code:
                                        break

                                key1 = 'cnt'

                                key2 = 'cnt'
                                if check_pipe_2['tipn'] in self.npoz_ignore_list:
                                    key1 = 'ckt'

                                    key2 = 'ckt'

                                G.add_edge(key_pipe['cnt'], check_pipe_2[key1])
                                selected_data = {key: key_pipe[key] for key in selected_keys}
                                used_pipes.append(selected_data)

                                node_label_by_id[key_pipe[key1]] = key_pipe['cnt']
                                node_label_by_id[check_pipe_2[key1]] = check_pipe_2[key2]

                                edge_labelz[(key_pipe['cnt'], check_pipe_2[key1])] = {'id': key_pipe['id'], 'edge': (
                                    key_pipe['cnt'], check_pipe_2[key1]),
                                                                                      }

                        else:

                            # G.add_edge(key_pipe['npo_idn'], key_pipe['npo_idk'])
                            G.add_edge(key_pipe['cnt'], key_pipe['ckt'])

                            selected_data = {key: key_pipe[key] for key in selected_keys}
                            used_pipes.append(selected_data)

                            node_label_by_id[key_pipe['npo_idn']] = key_pipe['cnt']
                            node_label_by_id[key_pipe['npo_idk']] = key_pipe['ckt']

                            edge_labelz[(key_pipe['cnt'], key_pipe['ckt'])] = {'id': key_pipe['id'], 'edge': (
                                key_pipe['cnt'], key_pipe['ckt']),
                                                                               }

                    if key in found_pipes and key_pipe['npo_idn'] == 0:
                        wrn_msg = 'Не идентифицировано начало трубы. Идентификатор: {ident}, наименование трубы: {cnam}'.format(
                            ident=key, cnam=key_pipe['cnam'])
                        logging.warning(wrn_msg)
            if found_pipes:
                found_pipes_idz += found_pipes
                found_pipes = []
            else:
                break
            iter += 1
            if iter > 1e+6: break

        def get_pipe_id(check_tuple):
            for el in edge_labelz:

                if el[0] == check_tuple[0] and el[1] == check_tuple[1]:
                    return edge_labelz[el]['id']

                if el[0] == check_tuple[1] and el[1] == check_tuple[0]:
                    return edge_labelz[el]['id']

        return G, edge_labelz, node_label_by_id, used_pipes

    def save_fig(self, G, edge_labelz, node_label_by_id, pic_name):
        '''формирование картинки для графа G'''

        spec_node_list = []

        for edge in G.edges():
            spec_node_list.append(edge[0])
            spec_node_list.append(edge[1])
        with open(os.path.join('input_data', 'pipe_values_ext.json'), 'r') as fc:
            dc = json.load(fc)

        label_dic = {val: val for val in spec_node_list}

        for item in edge_labelz:
            curr_id = str(edge_labelz[item]['id'])
            edge_labelz[item]['values'] = dc[curr_id]

        label_options = {"ec": "k", "fc": "white", "alpha": 0.7}

        edge_color_lst = [edge_labelz[edge_name]['values']['pressure'] for edge_name in edge_labelz]
        edge_values_dict = {edge_name: edge_labelz[edge_name]['values'] for edge_name in edge_labelz}

        # пока цвета ребер - значения давлений, минимальные - красные, зеленые - максимальные

        nx.draw_kamada_kawai(G, with_labels=True, node_size=self.node_size,
                             font_size=self.font_size, width=self.line_width - 4, labels=label_dic,
                             nodelist=spec_node_list,
                             font_weight=self.font_bold,
                             bbox=label_options,
                             edge_color='black', edge_cmap=plt.cm.RdYlGn)
        nt = net.Network(height='800px', width='100%', bgcolor=self.graph_bg_color, font_color=self.font_color)
        nt.from_nx(G)
        for e in nt.edges:
            e['width'] = self.line_width
        for n in nt.nodes:
            n["size"] = self.node_size
            n["font"] = {"size": self.font_size, "color": self.font_color, "font_face": 'Arial'}
            n["color"] = self.node_color
        for i, edge in enumerate(nt.edges):
            edge['color'] = 'red'

        def change_edge_color(g, param_name):

            medium_warn_color = 'e3c000'
            no_warn_color = '427043'
            warn_color = '7a1717'

            for edge in g.edges:
                if (edge["from"], edge["to"]) in edge_values_dict:
                    edge_id = (edge["from"], edge["to"])
                elif (edge["to"], edge["from"]) in edge_values_dict:
                    edge_id = (edge["to"], edge["from"])
                param_value = edge_values_dict[edge_id][param_name]
                edge['title'] = param_name + ': ' + str(param_value) + '\n date: ' + edge_values_dict[edge_id]['time']

                if param_name == 'pressure':
                    if self.optimal_pressure * (1 - self.press_deviation) <= float(
                            param_value) <= self.optimal_pressure * (
                            1 + self.press_deviation):
                        param_value = no_warn_color

                    elif self.optimal_pressure * (1 - 2 * self.press_deviation) <= float(
                            param_value) <= self.optimal_pressure * (
                            1 + 2 * self.press_deviation):
                        param_value = medium_warn_color


                    elif (param_value != medium_warn_color and param_value != no_warn_color) and (
                            float(param_value) >= self.optimal_pressure * (
                            1 + 2 * self.press_deviation) or float(param_value) <= self.optimal_pressure * (
                                    1 - 2 * self.press_deviation)):
                        param_value = warn_color

                elif param_name == 'debit':
                    if float(param_value) > self.optimal_debit:
                        param_value = no_warn_color
                    else:
                        param_value = medium_warn_color

                edge["color"] = param_value

        # change_edge_color(nt,'debit')
        # nt.write_html(os.path.join('data_html', pic_name[:-4] + '_debit' + '.html'))

        change_edge_color(nt, 'debit')
        nt.write_html(os.path.join('output_data/data_html', 'debits', pic_name[:-4] + '.html'))

        change_edge_color(nt, 'pressure')
        nt.write_html(os.path.join('output_data/data_html', 'pressures', pic_name[:-4] + '.html'))
        # draw_label = True
        # edge_label_dict = {}
        #
        # # if draw_label:
        # #
        # #     for edge_name in edge_labelz:
        # #         edge_label_dict[edge_name] = edge_labelz[edge_name]['values']['press']
        # #     edge_color_lst = [edge_labelz[edge_name]['values']['press'] for edge_name in edge_labelz]
        # #     nx.draw_networkx_edge_labels(G, pos=nx.kamada_kawai_layout(G), edge_color=edge_color_lst)

        figure = plt.gcf()  # get current figure
        figure.set_size_inches(30, 20)

        plt.savefig(os.path.join('output_data', pic_name))

    def draw_pipe_system(self, obj_id, single_pic=False):

        pipe_by_graph = defaultdict(lambda: [])
        pipes_info = {}
        if single_pic:
            self.single_pic = 1
            self.draw_wells = 0
        else:
            self.single_pic = 0
            self.draw_wells = 1
        selected_keys = ["id", "tipn", "tipk", "cnt", "ckt", "pipe_dat", "cnam", "npo_idn", "npo_idk", "agent"]
        used_pipes_lst = []
        '''отрисовка системы трубопровода'''

        if not self.pipe_data:
            err_msg = 'Отсутствуют данные по трубопроводам'
            print(err_msg)
            logging.error(err_msg)
            sys.exit()

        tube_with_obj_list = self.get_pipe_with_obj(obj_id)
        if tube_with_obj_list:

            total_G = None
            total_edge_labelz = {}
            total_node_label_by_id = {}

            for tube_with_obj in tube_with_obj_list:
                curr_pipe_data = self.pipe_data[tube_with_obj][0]
                selected_data = {key: curr_pipe_data[key] for key in selected_keys}
                if self.pipe_data[tube_with_obj][0]['tipn'] in self.npoz_ignore_list or \
                        self.pipe_data[tube_with_obj][0]['tipk'] in self.npoz_ignore_list: continue

                G, edge_labelz, node_label_by_id, curr_used_pipes = self.assemble_pipe_system(tube_with_obj)
                used_pipes_lst.append(selected_data)
                used_pipes_lst.extend(curr_used_pipes)

                if self.single_pic:
                    total_edge_labelz.update(edge_labelz)
                    total_node_label_by_id.update(node_label_by_id)
                    if total_G is None:
                        total_G = G
                    else:
                        total_G.update(G.edges, G.nodes)

                else:
                    pipe_nam = self.pipe_data[tube_with_obj][0]['cnam']
                    pic_name = 'Участок сети {pipe}.png'.format(npo_id=obj_id, pipe=str(pipe_nam))

                    self.save_fig(G, edge_labelz, node_label_by_id, pic_name)

                    for item in edge_labelz:
                        pipe_by_graph[pic_name].append(edge_labelz[item]['id'])

            if self.single_pic:
                if total_G is not None:
                    pic_name = 'Полная сеть для {npo_nam}.png'.format(
                        npo_nam=str(self.pipe_data[tube_with_obj][0]['ckt']))
                    self.save_fig(total_G, total_edge_labelz, total_node_label_by_id, pic_name)
            else:
                with open("input_data/pipe_by_graph.json", "w", encoding='utf-8') as json_file:
                    json.dump(dict(pipe_by_graph), json_file, ensure_ascii=False, indent=4, separators=(',', ': '))

            # print(used_pipes_lst)
            # data = {"data": used_pipes_lst}
            #
            # with open("input_data/output.json", "w", encoding='utf-8') as json_file:
            #     json.dump(data, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))
        else:
            wrn_msg = 'Для объекта НПО {} отсутствуют трубопроводы, содержащие данный объект.'.format(obj_id)
            print(wrn_msg)
            logging.error(wrn_msg)


def draw_system():
    pipe_drawing = pipeSystemDrawing()

    pipe_drawing.load_pipe_data()

    if pipe_drawing.obj_id != -1:
        pipe_drawing.npoz = [pipe_drawing.obj_id]
    else:
        pipe_drawing.get_all_npo()

    if pipe_drawing.npoz:
        for npo in pipe_drawing.npoz:
            print(npo)

            pipe_drawing.draw_pipe_system(npo, True)
            pipe_drawing.draw_pipe_system(npo)
    else:
        wrn_msg = 'Список товарных парков пуст.'
        print(wrn_msg)
        logging.error(wrn_msg)


if __name__ == '__main__':
    draw_system()
