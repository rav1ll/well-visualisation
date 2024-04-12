########################################################################
# pipe_system_drawing.py
# модуль для отрисовки системы трубопроводов
########################################################################

import os
import sys
import json
import logging

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import cm


class pipeSystemDrawing():

    def __init__(self):
        self.pipe_data = {}

        self.obj_id = -1
        self.pipes = []

        self.node_size = 7
        self.font_size = 11
        self.line_width = 1
        self.font_bold = 'normal'

        ##04082022_start
        self.single_pic = False
        ##04082022_end

        self.npok = 0
        self.labels = {}
        self.npoz_ignore_list = []

        self.mk_log()
        self.loadConfig()

        ##24052022_start
        self.npoz = None  # список ТП
        ##24052022_end

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
        if dc['font_bold']:
            self.font_bold = 'bold'

        # if self.obj_id == -1:

        ##12122022
        self.npoz_ignore_list = []
        npok = dc['npok']
        if npok == 0:
            self.npoz_ignore_list = [1, 7, 92]
        elif npok == 1:
            self.npoz_ignore_list = [1, 92]
        # self.npoz_ignore_list = []
        ##12122022

        self.single_pic = False
        single_pic = dc['single_pic']
        if single_pic == 1:
            self.single_pic = True

        ##04082022_start
        # label_dic = {0:{'nam':'L', 'armits_key':'len'}, 1:{'nam':'d', 'armits_key':'diam'}}
        label_dic = {0: {'nam': 'L', 'armits_key': 'len', 'si': 'м'}, 1: {'nam': 'd', 'armits_key': 'diam', 'si': 'мм'}}
        ##04082022_end

        label_list = dc['label_list']
        self.labels = {el: label_dic[el] for el in label_list if el in label_dic}

    def load_pipe_data(self):
        '''загрузка данных по трубопроводам из АРМИТС'''
        try:
            with open(os.path.join('input_data', 'pipe_data.json'), 'r', encoding='UTF-8') as fin:
                pipe_data = json.load(fin)['data']
                for val in pipe_data:

                    ##12122022
                    if val['tipn'] == 92: continue
                    ##12122022

                    if val['sost_t'] == 58 and val['agent'] in [106, 107, 108]:  # or val['sost_t'] == 51]
                        if val['id'] not in self.pipe_data:
                            self.pipe_data[val['id']] = []
                        self.pipe_data[val['id']].append(val)
                # self.pipe_data = [val for val in self.pipe_data if val['sost_t'] == 58 and val['agent'] in [106, 107, 108]]# or val['sost_t'] == 51]
        except BaseException as e:
            err_msg = 'Ошибка в загрузке данных по трубопроводам из КИС АРМИТС:\n{}'.format(e)
            print(err_msg)
            logging.error(err_msg)
            sys.exit()

    ##24052022_start
    def get_all_npo(self):
        '''сбор всех товарных парков'''
        self.npoz = {self.pipe_data[val][0]['npo_idk']: self.pipe_data[val][0]['ckt'] for val in self.pipe_data if
                     self.pipe_data[val][0]['tipn'] == 5 and self.pipe_data[val][0]['tipk'] == 10}

    def get_pipe_with_obj(self, obj_id):
        '''поиск трубы с заданным объектом'''

        ##08062022_start
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
        ##08062022_end

        return pipes_with_obj

    ##04082022_start
    def assemble_pipe_system(self, tube):
        ##04082022_end

        '''сбор трубопроводной сети'''
        node_label_by_id = {}
        edge_labelz = {}
        pipe = self.pipe_data[tube]

        found_pipes = [tube]
        found_pipes_idz = [tube]

        iter = 0
        plt.clf()

        G = nx.Graph()

        ##17082022_start
        # G.add_edge(self.pipe_data[tube][0]['npo_idn'], self.pipe_data[tube][0]['npo_idk'])
        G.add_edge(self.pipe_data[tube][0]['cnt'], self.pipe_data[tube][0]['ckt'])
        ##17082022_end

        node_label_by_id[self.pipe_data[tube][0]['npo_idn']] = self.pipe_data[tube][0]['cnt']
        node_label_by_id[self.pipe_data[tube][0]['npo_idk']] = self.pipe_data[tube][0]['ckt']

        ##17082022_start
        # edge_labelz[self.pipe_data[tube][0]['id']] = {'edge': (self.pipe_data[tube][0]['npo_idn'], self.pipe_data[tube][0]['npo_idk']), 'len': self.pipe_data[tube][-1]['int2'], 'diam':self.pipe_data[tube][0]['d_tr'] - 2*self.pipe_data[tube][0]['t_st']}
        edge_labelz[(self.pipe_data[tube][0]['cnt'], self.pipe_data[tube][0]['ckt'])] = {
            'id': self.pipe_data[tube][0]['id'],
            'edge': (self.pipe_data[tube][0]['cnt'], self.pipe_data[tube][0]['ckt']),
            'len': self.pipe_data[tube][-1]['int2'],
            'diam': self.pipe_data[tube][0]['d_tr'] - 2 * self.pipe_data[tube][0]['t_st']}
        ##17082022_end

        while 1:
            '''сбор труб с учетом нулевых идентификаторов, если сеть обрывается, выводим в лог сообщение'''
            for check_id in found_pipes_idz:
                check_pipe = self.pipe_data[check_id][0]
                if check_pipe['npo_idn'] == 0:
                    continue
                for key in self.pipe_data:
                    key_pipe = self.pipe_data[key][0]
                    if key_pipe['npo_idk'] == 0:
                        continue
                    if key in found_pipes or key in found_pipes_idz:
                        continue

                    ##12122022
                    # if (key_pipe['tipk'] == 122 and key_pipe['npo_idk'] == check_pipe['id']) or (
                    #         key_pipe['tipk'] != 122 and key_pipe['npo_idk'] == check_pipe['npo_idn']):
                    if (key_pipe['tipk'] == 122 and (
                            key_pipe['ckt'] == check_pipe['cnam'] or key_pipe['npo_idk'] == check_pipe['id'])) or (
                            key_pipe['tipk'] != 122 and key_pipe['ckt'] == check_pipe['cnt']):
                        # if (key_pipe['tipk'] == 122 and key_pipe['npo_idk'] == check_pipe['id']) or (
                        #         key_pipe['tipk'] != 122 and key_pipe['npo_idk'] == check_pipe['npo_idn']) or (
                        #         key_pipe['tipk'] == 122 and key_pipe['ckt'] == check_pipe['cnam']) or (
                        #         key_pipe['tipk'] != 122 and key_pipe['ckt'] == check_pipe['cnt']):
                        ##12122022

                        found_pipes.append(key)
                        if key_pipe['tipk'] == 122:
                            if check_pipe['tipk'] != 122:

                                ##17082022_start
                                # key1 = 'npo_idn'
                                key1 = 'cnt'
                                ##17082022_end

                                key2 = 'cnt'
                                if check_pipe['tipn'] in self.npoz_ignore_list:
                                    ##17082022_start
                                    # key1 = 'npo_idk'
                                    key1 = 'ckt'
                                    ##17082022_end

                                    key2 = 'ckt'

                                ##17082022_start
                                # G.add_edge(key_pipe['npo_idn'], check_pipe[key1])
                                G.add_edge(key_pipe['cnt'], check_pipe[key1])
                                ##17082022_end

                                node_label_by_id[key_pipe['npo_idn']] = key_pipe['cnt']
                                node_label_by_id[check_pipe[key1]] = check_pipe[key2]

                                ##17082022_start
                                # edge_labelz[key_pipe['id']] = {'edge': (key_pipe['npo_idn'], check_pipe[key1]), 'len': self.pipe_data[key][-1]['int2'], 'diam': key_pipe['d_tr'] - 2 * key_pipe['t_st']}
                                edge_labelz[(key_pipe['cnt'], check_pipe[key1])] = {'id': key_pipe['id'], 'edge': (
                                    key_pipe['cnt'], check_pipe[key1]),
                                                                                    'len': self.pipe_data[key][-1][
                                                                                        'int2'],
                                                                                    'diam': key_pipe['d_tr'] - 2 *
                                                                                            key_pipe['t_st']}
                                ##17082022_end

                            else:
                                vrez_id = check_pipe['npo_idk']
                                check_pipe_2 = self.pipe_data[vrez_id][0]

                                while check_pipe_2['tipk'] == 122:
                                    new_vrez_id = check_pipe_2['npo_idk']
                                    check_pipe_2 = self.pipe_data[new_vrez_id][0]
                                    if check_pipe_2['tipk'] != 122:
                                        break
                                ##17082022_start
                                # key1 = 'npo_idn'
                                key1 = 'cnt'
                                ##17082022_end

                                key2 = 'cnt'
                                if check_pipe_2['tipn'] in self.npoz_ignore_list:
                                    ##17082022_start
                                    # key1 = 'npo_idk'
                                    key1 = 'ckt'
                                    ##17082022_end

                                    key2 = 'ckt'

                                ##17082022_start
                                # G.add_edge(key_pipe['npo_idn'], check_pipe_2[key1])
                                G.add_edge(key_pipe['cnt'], check_pipe_2[key1])
                                ##17082022_end

                                node_label_by_id[key_pipe[key1]] = key_pipe['cnt']
                                node_label_by_id[check_pipe_2[key1]] = check_pipe_2[key2]

                                ##17082022_start
                                # edge_labelz[key_pipe['id']] = {'edge': (key_pipe['npo_idn'], check_pipe_2[key1]),
                                #                                'len': self.pipe_data[key][-1]['int2'],
                                #                                'diam': key_pipe['d_tr'] - 2 * key_pipe['t_st']}
                                edge_labelz[(key_pipe['cnt'], check_pipe_2[key1])] = {'id': key_pipe['id'], 'edge': (
                                    key_pipe['cnt'], check_pipe_2[key1]),
                                                                                      'len': self.pipe_data[key][-1][
                                                                                          'int2'],
                                                                                      'diam': key_pipe['d_tr'] - 2 *
                                                                                              key_pipe['t_st']}
                                ##17082022_end

                        else:

                            ##17082022_start
                            # G.add_edge(key_pipe['npo_idn'], key_pipe['npo_idk'])
                            G.add_edge(key_pipe['cnt'], key_pipe['ckt'])
                            ##17082022_end

                            node_label_by_id[key_pipe['npo_idn']] = key_pipe['cnt']
                            node_label_by_id[key_pipe['npo_idk']] = key_pipe['ckt']

                            ##17082022_start
                            # edge_labelz[key_pipe['id']] = {'edge': (key_pipe['npo_idn'], key_pipe['npo_idk']), 'len': self.pipe_data[key][-1]['int2'], 'diam': key_pipe['d_tr'] - 2 * key_pipe['t_st']}
                            edge_labelz[(key_pipe['cnt'], key_pipe['ckt'])] = {'id': key_pipe['id'], 'edge': (
                                key_pipe['cnt'], key_pipe['ckt']),
                                                                               'len': self.pipe_data[key][-1]['int2'],
                                                                               'diam': key_pipe['d_tr'] - 2 * key_pipe[
                                                                                   't_st']}
                            ##17082022_end

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

                ##17082022_start
                # val = edge_labelz[el]['edge']
                # if val[0] == check_tuple[0] and val[1] == check_tuple[1]:
                if el[0] == check_tuple[0] and el[1] == check_tuple[1]:
                    # return el
                    return edge_labelz[el]['id']

                # if val[0] == check_tuple[1] and val[1] == check_tuple[0]:
                if el[0] == check_tuple[1] and el[1] == check_tuple[0]:
                    # return el
                    return edge_labelz[el]['id']
                ##17082022_end

        to_remove_edges = []
        for edge in G.edges():

            pipe_id = get_pipe_id(edge)

            # if self.pipe_data[pipe_id][0]['tipn'] == 122 or (
            #         self.pipe_data[pipe_id][0]['tipn'] == 122 and self.pipe_data[pipe_id][0]['tipk'] == 122) or \
            #         self.pipe_data[pipe_id][0]['tipn'] in self.npoz_ignore_list or self.pipe_data[pipe_id][0][
            #     'tipk'] in self.npoz_ignore_list or self.pipe_data[pipe_id][0]['npo_idn'] == self.pipe_data[pipe_id][0][
            #     'npo_idk']:
            #     to_remove_edges.append(edge)
            #     to_remove_nodes.append(edge[0])
            #     to_remove_nodes.append(edge[1])

                ##17082022_start
                # edge_labelz.pop(pipe_id)
                ##17082022_edge

        if to_remove_edges:
            G.remove_edges_from(to_remove_edges)
        # if to_remove_nodes:
        #     G.remove_nodes_from(to_remove_nodes)
        return G, edge_labelz, node_label_by_id

    def save_fig(self, G, edge_labelz, node_label_by_id, pic_name):
        '''формирование картинки для графа G'''

        spec_node_list = []
        for edge in G.edges():
            spec_node_list.append(edge[0])
            spec_node_list.append(edge[1])
        # spec_node_list = [val for val in G.nodes()]

        ##17082022_start
        # label_dic = {val: node_label_by_id[val] for val in spec_node_list}
        label_dic = {val: val for val in spec_node_list}
        ##17082022_end

        label_options = {"ec": "k", "fc": "white", "alpha": 0.7}

        nx.draw_kamada_kawai(G, with_labels=True, node_size=self.node_size,
                             font_size=self.font_size, width=self.line_width, labels=label_dic, nodelist=spec_node_list,
                             font_weight=self.font_bold,
                             bbox=label_options)  # , edge_color=[1,1,1], edge_cmap = cm.Blues)

        if self.labels:

            edge_label_list = {}
            for val in edge_labelz:
                edge = edge_labelz[val]['edge']
                if edge not in G.edges():
                    continue
                label_str = ''
                for no in self.labels:
                    nam = self.labels[no]['nam']
                    armits_key = self.labels[no]['armits_key']

                    ##17082022_start
                    # label_str += '{el}={val}\n'.format(el = nam, val = edge_labelz[val][armits_key])
                    label_str += '{el}={val} {si}\n'.format(el=nam, val=edge_labelz[val][armits_key],
                                                            si=self.labels[no]['si'])
                    ##17082022_end

                edge_label_list[edge_labelz[val]['edge']] = label_str
            nx.draw_networkx_edge_labels(G, pos=nx.kamada_kawai_layout(G), edge_labels=edge_label_list)

        figure = plt.gcf()  # get current figure
        figure.set_size_inches(20, 15)
        # plt.show()
        # plt.savefig(os.path.join('output_data', '{}.png'.format(str(self.obj_id))) )#, dpi=150)

        ##04082022_start
        plt.savefig(os.path.join('output_data', pic_name))  # , dpi=150)
        ##04082022_end

    def draw_pipe_system(self, obj_id):

        '''отрисовка системы трубопровода'''
        # self.load_pipe_data()

        # self.assemble_pipe_system(1515, 5491)
        # return

        if not self.pipe_data:
            err_msg = 'Отсутствуют данные по трубопроводам'
            print(err_msg)
            logging.error(err_msg)
            sys.exit()

        tube_with_obj_list = self.get_pipe_with_obj(obj_id)
        if tube_with_obj_list:

            ##04082022_start
            total_G = None
            total_edge_labelz = {}
            total_node_label_by_id = {}

            for tube_with_obj in tube_with_obj_list:
                if self.pipe_data[tube_with_obj][0]['tipn'] in self.npoz_ignore_list or \
                        self.pipe_data[tube_with_obj][0]['tipk'] in self.npoz_ignore_list: continue

                G, edge_labelz, node_label_by_id = self.assemble_pipe_system(tube_with_obj)
                if self.single_pic:
                    total_edge_labelz.update(edge_labelz)
                    total_node_label_by_id.update(node_label_by_id)
                    if total_G == None:
                        total_G = G
                    else:
                        total_G.update(G.edges, G.nodes)
                else:
                    pipe_nam = self.pipe_data[tube_with_obj][0]['cnam']
                    pic_name = '{npo_id}_{pipe}.png'.format(npo_id=obj_id, pipe=str(pipe_nam))
                    self.save_fig(G, edge_labelz, node_label_by_id, pic_name)
            if self.single_pic:
                if total_G != None:
                    pic_name = '{npo_id}_{npo_nam}.png'.format(npo_id=obj_id,
                                                               npo_nam=str(self.pipe_data[tube_with_obj][0]['ckt']))
                    self.save_fig(total_G, total_edge_labelz, total_node_label_by_id, pic_name)

            ##04082022_end

        else:
            wrn_msg = 'Для объекта НПО {} отсутствуют трубопроводы, содержащие данный объект.'.format(obj_id)
            print(wrn_msg)
            logging.error(wrn_msg)


if __name__ == '__main__':

    pipe_drawing = pipeSystemDrawing()
    ##24052022_start
    pipe_drawing.load_pipe_data()

    if pipe_drawing.obj_id != -1:
        pipe_drawing.npoz = [pipe_drawing.obj_id]
    else:
        pipe_drawing.get_all_npo()


    if pipe_drawing.npoz:
        for npo in pipe_drawing.npoz:
            print(npo)
            pipe_drawing.draw_pipe_system(npo)
    else:
        wrn_msg = 'Список товарных парков пуст.'
        print(wrn_msg)
        logging.error(wrn_msg)
    ##24052022_end