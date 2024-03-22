import time
import logging
import xlsxwriter
import pickle
import math

import matplotlib.pyplot as plt



# 29032021_end

class stress_tester(object):
    '''проверка трубопроводной сети по заданному товарному парку'''

    def __init__(self):
        self.data_class = stress_tester_io()
        self.break_npo = [4, 5, 6, 10, 14, 174]
        self.end_pipes = []  # список конечных труб, которые приходят в указаный ТП
        self.pipes = []  # список словарей идентификатор:наименование труб, которые входят в сеть (каждый элемент - список, тк в один тп приходят несколько труб)
        self.wells = []  # список словарей идентификатор:наименование скважин, которые входят в сеть
        self.npo = []  # список словарей идентификатор:наименование насосов, которые входят в сеть и для которых вручную будут задаваться параметры

        self.park_name = ''

        self.zero_debit = {}

        self.next_to_tp = {}  # словарь последовательности труб до след парка

        ##17022021_start
        self.next_to_tp_vrz = {}  # словарь труб, которые врезаются в сторону товарного парка
        ##17022021_end

    def find_end_pipes(self):
        '''поиск идентификаторов труб, которые приходят в указанный ТП'''

        self.end_pipes = [self.data_class.pipe_data_dic[tube][0]['id'] for tube in self.data_class.pipe_data_dic if
                          self.data_class.pipe_data_dic[tube][0]['npo_idk'] == self.data_class.park_id]

        print(self.end_pipes)

        ##25112020_start
        if not self.end_pipes:
            err_msg = 'Не найден трубопровод, содержащий заданный товарный парк, так как отсутствует труба, у которой конец совпадает с заданным товарным парком.'
            # print(err_msg)
            logging.error(err_msg)
            raise Exception(err_msg)
        ##25112020_end

    def assemble_pipe_system(self):
        obj_lst = []
        obj_nm = []
        pipes_lst = []
        '''сбор трубопроводной сети для указанного ТП'''
        self.find_end_pipes()

        end_pipez = self.end_pipes.copy()
        for iPipe in range(len(end_pipez)):
            tube = end_pipez[iPipe]
            pipe = self.data_class.pipe_data_dic[tube]
            # врезки
            found_pipes = [tube]
            found_pipes_idz = [tube]
            iter = 0

            print('found pipes:', found_pipes)

            while 1:
                # сбор труб с учетом нулевых идентификаторов, если сеть обрывается, выводим в лог сообщение
                for check_id in found_pipes_idz:
                    check_pipe = self.data_class.pipe_data_dic[check_id][0]
                    if check_pipe['npo_idn'] == 0:
                        continue
                    for key in self.data_class.pipe_data_dic:
                        key_pipe = self.data_class.pipe_data_dic[key][0]
                        if key_pipe['npo_idk'] == 0: continue;
                        if key in found_pipes or key in found_pipes_idz: continue
                        if (key_pipe['tipk'] == 122 and key_pipe['npo_idk'] == check_pipe['id']) or (
                                key_pipe['tipk'] != 122 and key_pipe['npo_idk'] == check_pipe['npo_idn']):
                            found_pipes.append(key)

                            if key_pipe["ckt"] not in obj_lst:
                                obj_lst.append(key_pipe['ckt'])

                            if key_pipe["npo_idk"] not in obj_nm:
                                obj_nm.append(key_pipe['npo_idk'])




                            # print(key_pipe["cnt"])
                        if key in found_pipes and key_pipe['npo_idn'] == 0:
                            print(key, self.data_class.pipe_data_dic[key][0]['cnam'])

                            ##25112020_start
                            wrn_msg = 'Не идентифицировано начало трубы с идентификатором: {ident}, наименование: {cnam}'.format(
                                ident=key, cnam=key_pipe['cnam'])
                            ##25112020_end

                            # print(wrn_msg)
                            logging.warning(wrn_msg)


                # более быстрый вариант, но без вывода сообщений в лог
                # found_pipes = {key  for check_id in found_pipes for key in self.data_class.pipe_data_dic if key not in found_pipes_idz and (self.data_class.pipe_data_dic[key][0]['npo_idk'] == self.data_class.pipe_data_dic[check_id][0]['id'] or (self.data_class.pipe_data_dic[key][0]['npo_idk'] != 0 and self.data_class.pipe_data_dic[check_id][0]['npo_idn'] != 0 and self.data_class.pipe_data_dic[key][0]['npo_idk'] == self.data_class.pipe_data_dic[check_id][0]['npo_idn']) )}
                # found_pipes = {key for check_id in found_pipes for key in self.data_class.pipe_data_dic if key not in found_pipes_idz and (self.data_class.pipe_data_dic[key][0]['npo_idk'] == self.data_class.pipe_data_dic[check_id][0]['id'] or self.data_class.pipe_data_dic[key][0]['npo_idk'] == self.data_class.pipe_data_dic[check_id][0]['npo_idn'])}
                if found_pipes:
                    found_pipes_idz += found_pipes
                    found_pipes = []
                else:
                    break
                iter += 1
                if iter > 1e+6: break

            wellz = {self.data_class.pipe_data_dic[tube][0]['npo_idn']: [self.data_class.pipe_data_dic[tube][0]['cnam'],
                                                                         tube] for tube in found_pipes_idz if
                     self.data_class.pipe_data_dic[tube][0]['tipn'] == 1}
            # wellz = {self.data_class.pipe_data_dic[tube][0]['npo_idn']:self.data_class.pipe_data_dic[tube][0]['cnam'].split(' - ')[0] for tube in found_pipes_idz if self.data_class.pipe_data_dic[tube][0]['tipn'] == 1}
            if not len(wellz.keys()):
                self.end_pipes.remove(tube)
                continue
            self.wells += [wellz]
            self.pipes += [{tube: self.data_class.pipe_data_dic[tube][0]['cnam'] for tube in found_pipes_idz}]
            npo_id = {self.data_class.pipe_data_dic[tube][0]['npo_idk']: self.data_class.pipe_data_dic[tube][0]['cnam']
                      for tube in found_pipes_idz if self.data_class.pipe_data_dic[tube][0]['tipk'] in self.break_npo}
            npo_id.update(
                {self.data_class.pipe_data_dic[tube][0]['npo_idn']: self.data_class.pipe_data_dic[tube][0]['cnam'] for
                 tube in found_pipes_idz if self.data_class.pipe_data_dic[tube][0]['tipn'] in self.break_npo and
                 self.data_class.pipe_data_dic[tube][0]['npo_idn'] not in npo_id})
            self.npo += [npo_id]

        if len(self.npo):
            npoz = set([npo for i in range(len(self.npo)) for npo in self.npo[i]])

            ##25112020_start
            # info_msg = 'Необходимо задать параметры для следующего списка объектов НПО: {}.'.format(str(npoz))
            ##print(info_msg)
            # logging.info(info_msg)
            ##25112020_end


    def add_new_section(self, pipe_id, incut):
        '''добавление участка с учетом врезки'''
        pipe = self.data_class.pipe_data_dic[pipe_id].copy()
        iSect = 0
        while 1:
            if incut > pipe[iSect]['int1'] and incut < pipe[iSect]['int2']:
                pipe.insert(iSect + 1, pipe[iSect].copy())
                pipe.insert(iSect + 2, pipe[iSect].copy())
                pipe[iSect + 1]['int2'] = incut
                pipe[iSect + 2]['int1'] = incut
                pipe[iSect + 1]['length'] = pipe[iSect + 1]['int2'] - pipe[iSect + 1]['int1']
                pipe[iSect + 2]['length'] = pipe[iSect + 2]['int2'] - pipe[iSect + 2]['int1']
                pipe.pop(iSect)
                self.data_class.pipe_data_dic[pipe_id] = pipe
                break
            iSect += 1
            if iSect >= len(pipe):
                break

    def set_vrez_point(self, id_tube, vrez_point_no, vrez_tube_id):
        '''записываем номер интервала трубы, в которую врезана труба с идентификатором id_tube'''
        for i in range(len(self.data_class.pipe_data_dic[id_tube])):
            self.data_class.pipe_data_dic[id_tube][i]['vrez_point'] = vrez_point_no
            self.data_class.pipe_data_dic[id_tube][i]['vrez_id'] = vrez_tube_id

    def add_vrez_points(self):
        '''восстановление точек врезки и распределение дебита с учетом этих точек'''
        # для собранных труб найдем места врезок и вставим новые точки на участках врезки
        for tubez in self.pipes:
            for tube in tubez:
                first_sect = self.data_class.pipe_data_dic[tube][0]
                vrez_len = first_sect['vrez']
                id_vrez = first_sect['npo_idk']
                if vrez_len and first_sect['tipk'] == 122 and id_vrez in self.data_class.pipe_data_dic:
                    self.add_new_section(id_vrez, vrez_len)

        # после того как новые секции с учетом мест врезки для труб добавлены,записываем номер интервала врезки и перераспределяем дебет по участкам с учетом врезок

        ##25112020_start
        wrn_msg = ''
        ##25112020_end

        for tubez in self.pipes:
            for tube in tubez:
                first_sect = self.data_class.pipe_data_dic[tube][0]
                debit = first_sect['qg']
                vrez_tube_id = -1
                if first_sect['qg_vrez'] > 0:
                    debit = first_sect['qg_vrez']
                if first_sect['tipk'] == 122:
                    vrez_tube_id = first_sect['npo_idk']
                    if vrez_tube_id not in self.data_class.pipe_data_dic: continue
                    vrez_tube = self.data_class.pipe_data_dic[vrez_tube_id]
                    if first_sect['vrez'] > vrez_tube[-1]['int2']:
                        vrez_point_no = -1

                        ##25112020_start
                        wrn_msg += str(first_sect['id']) + '\t' + str(first_sect['cnam']) + '\t' + str(
                            vrez_tube[0]['id']) + '\t' + str(vrez_tube[0]['cnam']) + '\n'
                        ##25112020_end

                    elif first_sect['vrez'] < vrez_tube[0]['int1']:
                        vrez_point_no = 0
                    else:  # получаем номер интервала, если место врезки совпадает с началом интервала
                        vrez_point_no = [i for i in range(len(vrez_tube)) if
                                         vrez_tube[i]['int1'] <= first_sect['vrez'] <= vrez_tube[i]['int2']][0]

                    # перераспределяем дебит по участкам с учетом мест врезок

                    if vrez_point_no == -1:  # если врезка в крайнем справа участке, то дебит врезки только ему добавляем, при условии, что врезка не в конце трубпоровода
                        if first_sect['vrez'] != vrez_tube[-1]['int2']:
                            vrez_tube[vrez_point_no]['debit'] += debit
                    else:
                        for j_int in range(vrez_point_no, len(vrez_tube)):
                            vrez_tube[j_int]['debit'] += debit

                    ##17022021_start
                    self.set_vrez_point(tube, vrez_point_no, vrez_tube_id)
                ##else: # если место врезки не труба, а объект НПО, то end_pres будем брать с начала трубы, а дебит из исходных полей
                ##    vrez_point_no = 0
                ##    if first_sect['id'] not in self.end_pipes:
                ##    #if first_sect['id'] != self.end_pipe:
                ##        vrez_tube_list = [idtube for idtube in tubez if first_sect['npo_idk'] == self.data_class.pipe_data_dic[idtube][0]['npo_idn']]
                ##        if not vrez_tube_list: continue
                ##        vrez_tube_id = vrez_tube_list[0]
                ##        vrez_tube = self.data_class.pipe_data_dic[vrez_tube_id]
                ##        for j_int in range(len(vrez_tube)):
                ##            vrez_tube[j_int]['debit'] += debit
                ##17022021_end

        ##25112020_start
        if wrn_msg:
            wrn_msg = ('Трубы, у которых место врезки больше длины трубы, ' +
                       'в которую она врезана.\nидентификатор\tнаименование\tидентификатор ' +
                       'места врезки\tнаименование места врезки\n') + wrn_msg
            logging.warning(wrn_msg)
            ##25112020_end

    def run_first_step(self):
        '''I этап работы микросервиса'''
        # сбор трубопроводной сети, вывод списка объектов, для которых необходимо вручную задать входное давление,
        # вывод списка скважин, попадающих в собранную сеть, для которых необходимо задать коэффициент прогноза,
        # вывод сообщений, если будут найдены скважины, неотождествленные с Геокаталогом или трубы, у которых не иденцифицирован конец
        # загружаем данные существующих трубопроводов

        self.data_class.load_pipe_data()
        # проверяем концы загруженных трубопроводов (для случая, если понадобится предварительно проверить всю выгрузку)
        # self.data_class.check_loaded_pipes()
        # собираем трубпороводную сеть по заданному ТП
        # self.assemble_pipe_system()

        self.assemble_pipe_system()
        if self.pipes:
            self.add_vrez_points()
        else:

            ##25112020_start
            err_msg = 'Для заданного товарного парка не удалось собрать трубопроводную сеть'
            ##25112020_end

            print(err_msg)
            logging.error(err_msg)
            raise Exception(err_msg)

    def main_func(self):
        '''главный загрузчик микросервиса'''

        self.run_first_step()


if __name__ == '__main__':
    calc_class = stress_tester()
    calc_class.main_func()