# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GeoINCRA
                                 A QGIS plugin
 Georreferenciamento de Imóveis Rurais
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-02-13
        copyright            : (C) 2022 by Tiago Prudencio e Leandro França
        email                : contato@geoone.com.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Tiago Prudencio e Leandro França'
__date__ = '2024-08-10'
__copyright__ = '(C) 2024 by Tiago Prudencio e Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from PyQt5.QtCore import *
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsWkbTypes,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingParameterFile,
                       QgsVectorLayer,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsGeometry,
                       QgsLineString,
                       QgsMultiPolygon,
                       QgsPolygon,
                       QgsPoint,
                       QgsProcessingParameterFeatureSink)
from qgis import processing
from qgis.PyQt.QtGui import QIcon
from GeoINCRA.images.Imgs import *
import os


class LayersFromSheet(QgsProcessingAlgorithm):

    ODS = 'ODS'
    VERTICE = 'VERTICE'
    LIMITE = 'LIMITE'
    PARCELA = 'PARCELA'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LayersFromSheet()

    def name(self):
        return 'LayersFromSheet'.lower()

    def displayName(self):

        return self.tr('Importar planilha ODS')

    def group(self):

        return self.tr(self.groupId())

    def groupId(self):

        return ''

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/geoincra_pb.png'))

    def shortHelpString(self):
        txt = 'Esta ferramenta importa uma <b>Planilha ODS</b> no padrão do SIGEF/INCRA, carregando as camadas vétice (ponto), limite (linha) e parcela (polígono) no modelo GeoRural.'
        footer = '''<div>
                      <div align="center">
                      <img style="width: 100%; height: auto;" src="data:image/jpg;base64,'''+ INCRA_GeoOne +'''
                      </div>
                      <div align="right">
                      <p align="right">
                      <a href="https://geoone.com.br/pvgeoincra2/"><span style="font-weight: bold;">Conheça o curso de GeoINCRA no QGIS</span></a>
                      </p>
                      <p align="right">
                      <a href="https://portal.geoone.com.br/m/lessons/georreferenciamento-de-imveis-rurais-com-o-plugin-geoincra-1690158094835"><span style="font-weight: bold;">Acesse seu curso na GeoOne</span></a>
                      </p>
                      <a target="_blank" rel="noopener noreferrer" href="https://geoone.com.br/"><img title="GeoOne" src="data:image/png;base64,'''+ GeoOne +'''"></a>
                      <p><i>"Mapeamento automatizado, fácil e direto ao ponto é na GeoOne!"</i></p>
                      </div>
                    </div>'''
        return txt + footer

    def initAlgorithm(self, config=None):

        self.addParameter(
        QgsProcessingParameterFile(
            self.ODS,
            self.tr('Planilha ODS do Sigef'),
            fileFilter= 'Planilha ODF (*.ods)'
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.VERTICE,
                self.tr('Vértices da planilha')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.LIMITE,
                self.tr('Limites da planilha')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.PARCELA,
                self.tr('Parcela da planilha')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        fonte = self.parameterAsString(
            parameters,
            self.ODS,
            context
        )

        if fonte is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.ODS))

        layer = QgsVectorLayer(fonte+'|layername=perimetro_1', "planilha", "ogr")
        if not layer.isValid():
            raise QgsProcessingException("Erro ao carregar a planilha ODS!")

        # Verificar número de perímetros da ODS
        cont = 1
        while layer.isValid():
            cont += 1
            layer = QgsVectorLayer(fonte + '|layername=perimetro_' + str(cont), "planilha", "ogr")
        num_tab = cont - 1

        # Pegar dados do imóvel
        feedback.pushInfo('Obtendo dados da planilha ODS...')
        idendificacao = QgsVectorLayer(fonte+'|layername=identificacao', "planilha", "ogr")
        dic_nat_ser = {'Particular':1, 'Contrato com Administração Pública':2}
        dic_pessoa, dic_situacao  = {'Física':1, 'Jurídica':2}, {'Imóvel Registrado':1, 'Área Titulada não Registrada':2, 'Área não Titulada':3}
        dic_natureza = {'Assentamento':1,'Assentamento Parcela':2,'Estrada':3,'Ferrovia':4,'Floresta Pública':5,'Gleba Pública':6,'Particular':7,'Perímetro Urbano':8,'Terra Indígena':9,'Terreno de Marinha':10,'Terreno Marginal':11,'Território Quilombola':12,'Unidade de Conservação':13}
        for k, lin in enumerate(idendificacao.getFeatures()):
            valor = str(lin[1]).replace('NULL','')
            if k == 5:
                nome = valor
            elif k == 1:
                nat_serv = dic_nat_ser[valor]
            elif k == 4:
                pessoa = dic_pessoa[valor]
            elif k == 10:
                situacao = dic_situacao[valor]
            elif k == 11:
                natureza = dic_natureza[valor]
            elif k == 6:
                cpf_cnpj = valor
            elif k == 9:
                denominacao = valor
            elif k == 12:
                sncr = valor
            elif k == 13:
                cod_cartorio = valor
            elif k == 14:
                matricula_parcela = valor
            elif k == 16:
                try:
                    municipio = valor.split('-')[0]
                    uf = valor.split('-')[1]
                except:
                    municipio = ''
                    uf = ''

        # Pegar dados de SRC do perímetro
        feedback.pushInfo('Lendo dados de SRC...')
        layer = QgsVectorLayer(fonte+'|layername=perimetro_1', "planilha", "ogr")
        lista = []
        for k, lin in enumerate(layer.getFeatures()):
            if k == 4:
                lado = lin[1]
            elif k == 8:
                src = lin[1]
                mc = float(lin[3])
                hemisf = lin[5]

        # Sistema de Referência de Coordenadas
        if src == 'Geográfica':
            SRC = QgsCoordinateReferenceSystem('EPSG:4674')
        else:
            fuso = round((183+mc)/6)
            if hemisf[0].upper() == 'S':
                SRC = QgsCoordinateReferenceSystem('EPSG:' + str(31960+fuso))
            elif hemisf[0].upper() == 'N':
                SRC = QgsCoordinateReferenceSystem('EPSG:' + str(31954+fuso))
        feedback.pushInfo('O SRC da planilha é {}'.format(SRC.authid()))

        # Criar camada de Pontos
        feedback.pushInfo('Criando camada Vértice...')
        Fields1 = QgsFields()
        itens  = {   'indice': QVariant.Int,
                     'vertice': QVariant.String,
                     'tipo_verti': QVariant.String,
                     'metodo_pos' : QVariant.String,
                     'sigma_x' : QVariant.Double,
                     'sigma_y' : QVariant.Double,
                     'sigma_z' : QVariant.Double,
                     }
        for item in itens:
            Fields1.append(QgsField(item, itens[item]))

        (sink1, dest_id1) = self.parameterAsSink(
            parameters,
            self.VERTICE,
            context,
            Fields1,
            QgsWkbTypes.PointZ,
            SRC
        )
        if sink1 is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.VERTICE))

        # Criar camada de Linhas
        feedback.pushInfo('Criando camada Limite...')
        Fields2 = QgsFields()
        itens  = {   'tipo': QVariant.String,
                     'confrontan': QVariant.String,
                     'cns': QVariant.String,
                     'matricula' : QVariant.String,
                     }
        for item in itens:
            Fields2.append(QgsField(item, itens[item]))

        (sink2, dest_id2) = self.parameterAsSink(
            parameters,
            self.LIMITE,
            context,
            Fields2,
            QgsWkbTypes.LineStringZ,
            SRC
        )
        if sink2 is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.LIMITE))


        # Criar camada de Polígono
        feedback.pushInfo('Criando camada Parcela...')
        Fields3 = QgsFields()
        itens  = {   'nome': QVariant.String,
                     'nat_serv': QVariant.Int,
                     'pessoa': QVariant.Int,
                     'cpf_cnpj' : QVariant.String,
                     'denominacao': QVariant.String,
                     'situacao': QVariant.Int,
                     'natureza': QVariant.Int,
                     'sncr': QVariant.String,
                     'matricula': QVariant.String,
                     'cod_cartorio': QVariant.String,
                     'municipio': QVariant.String,
                     'uf': QVariant.String,
                     'resp_tec': QVariant.String,
                     'reg_prof': QVariant.String,
                     'data': QVariant.Date,
                     }
        for item in itens:
            Fields3.append(QgsField(item, itens[item]))

        (sink3, dest_id3) = self.parameterAsSink(
            parameters,
            self.PARCELA,
            context,
            Fields3,
            QgsWkbTypes.MultiPolygonZ,
            SRC
        )
        if sink3 is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.PARCELA))

        for tabela in range(num_tab):

            layer = QgsVectorLayer(fonte+'|layername=perimetro_{}'.format(tabela+1), "planilha", "ogr")
            lista = []
            for k, lin in enumerate(layer.getFeatures()):
                if k > 10:
                    lista += [lin.attributes()]


            feedback.pushInfo('Alimentando camada Vértice (pontos) do Perímetro {}...'.format(tabela+1))
            cont = 0
            pnts = []
            for item in lista:
                if src == 'Geográfica':
                    lon = item[1].replace(',','.').split(' ')
                    X = (float(lon[0]) + float(lon[1])/60 + float(lon[2])/3600)*(-1 if lon[3] == 'W' else 1)
                    lat = item[3].replace(',','.').split(' ')
                    Y = (float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600)*(-1 if lat[3] == 'S' else 1)
                else:
                    X = float(item[1].replace(',','.'))
                    Y = float(item[3].replace(',','.'))
                Z = float(item[5].replace(',','.'))
                feat = QgsFeature(Fields1)
                pnts += [QgsPoint(X,Y,Z)]
                feat.setGeometry(QgsGeometry(QgsPoint(X,Y,Z)))
                cont += 1
                feat['indice'] = cont
                codigo = str(item[0])
                feat['vertice'] = codigo
                feat['tipo_verti'] = codigo.split('-')[1]
                feat['metodo_pos'] = str(item[7])
                feat['sigma_x'] = float(item[2].replace(',','.'))
                feat['sigma_y'] = float(item[4].replace(',','.'))
                feat['sigma_z'] = float(item[6].replace(',','.'))
                sink1.addFeature(feat, QgsFeatureSink.FastInsert)
                if feedback.isCanceled():
                    break


            feedback.pushInfo('Alimentando camada Limite (linha) do Perímetro {}...'.format(tabela+1))
            linha = []
            anterior_cns = str(lista[0][9]).replace('NULL','')
            anterior_mat = str(lista[0][10]).replace('NULL','')
            anterior_confr = str(lista[0][11]).replace('NULL','')

            for k, item in enumerate(lista):
                linha += [pnts[k]]
                cns = str(item[9]).replace('NULL','')
                matricula = str(item[10]).replace('NULL','')
                confrontante = str(item[11]).replace('NULL','')
                if ((cns+matricula+confrontante) != (anterior_cns+anterior_mat+anterior_confr)):
                    feat = QgsFeature(Fields2)
                    feat.setGeometry(QgsGeometry(QgsLineString(linha)))
                    feat['tipo'] = str(item[8])
                    feat['confrontan'] = anterior_confr
                    feat['cns'] = anterior_cns
                    feat['matricula'] = anterior_mat
                    sink2.addFeature(feat, QgsFeatureSink.FastInsert)
                    anterior_mat = matricula
                    anterior_cns = cns
                    anterior_confr = confrontante
                    linha = [pnts[k]]
                if feedback.isCanceled():
                    break

            # Último segmento
            feat = QgsFeature(Fields2)
            if (cns+matricula+confrontante) == (anterior_cns+anterior_mat+anterior_confr):
                linha += [pnts[0]]
                feat['tipo'] = str(item[8])
                feat['confrontan'] = anterior_confr
                feat['cns'] = anterior_cns
                feat['matricula'] = anterior_mat
            else:
                linha = [pnts[k], pnts[0]]
                feat['tipo'] = str(item[8])
                feat['confrontan'] = confrontante
                feat['cns'] = cns
                feat['matricula'] = matricula
            feat.setGeometry(QgsGeometry(QgsLineString(linha)))
            sink2.addFeature(feat, QgsFeatureSink.FastInsert)


            feedback.pushInfo('Alimentando camada Parcela (polígono) do Perímetro {}...'.format(tabela+1))
            feat = QgsFeature(Fields3)
            feat['nome'] = nome
            feat['nat_serv'] = nat_serv
            feat['pessoa'] = pessoa
            feat['cpf_cnpj'] = cpf_cnpj
            feat['denominacao'] = denominacao
            feat['situacao'] = situacao
            feat['natureza'] = natureza
            feat['sncr'] = sncr
            feat['matricula'] = matricula_parcela
            feat['cod_cartorio'] = cod_cartorio
            feat['municipio'] = municipio
            feat['uf'] = uf
            mPol = QgsMultiPolygon()
            anel = QgsLineString(pnts+[pnts[0]])
            pol = QgsPolygon(anel)
            mPol.addGeometry(pol)
            newGeom = QgsGeometry(mPol)
            feat.setGeometry(newGeom)
            sink3.addFeature(feat, QgsFeatureSink.FastInsert)

        return {self.VERTICE: dest_id1,
                self.LIMITE: dest_id2,
                self.PARCELA: dest_id3}
