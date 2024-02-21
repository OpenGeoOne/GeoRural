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
__date__ = '2022-07-10'
__copyright__ = '(C) 2022 by Tiago Prudencio e Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsFeature,
                       QgsSettings,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterVectorLayer)

from qgis.PyQt.QtGui import QIcon
from GeoINCRA.images.Imgs import *
import os


class FillCodes(QgsProcessingAlgorithm):

    def tr(self, string):

        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return FillCodes()

    def name(self):

        return 'fillcodes'

    def displayName(self):

        return self.tr('Preencher código do vértice')

    def group(self):

        return self.tr(self.groupId())

    def groupId(self):

        return ''

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/geoincra_pb.png'))

    def shortHelpString(self):
        txt = '''Esta ferramenta preenche automaticamente o atributo "código do vértice" da camada "vértice", inserindo-se uma única vez o código do credenciado e o número inicial para cada tipo de vértice.
        Obs.: É necessário que o campo "ordem do vértice" esteja preenchido corretamente.'''

        footer = '''<div>
                      <div align="center">
                      <img style="width: 100%; height: auto;" src="data:image/jpg;base64,'''+ INCRA_GeoOne +'''
                      </div>
                      <div align="right">
                      <p align="right">
                      <a href="https://github.com/OpenGeoOne/GeoINCRA/wiki/Sobre-o-GeoINCRA#banco-de-dados-georural"><span style="font-weight: bold;">Clique aqui para conhecer o modelo <b>GeoRural</b></span></a><br>
                      </p>
                      <a target="_blank" rel="noopener noreferrer" href="https://geoone.com.br/"><img title="GeoOne" src="data:image/png;base64,'''+ GeoOne +'''"></a>
                      <p><i>"Mapeamento automatizado, fácil e direto ao ponto é na GeoOne!"</i></p>
                      </div>
                    </div>'''
        return txt + footer

    VERTICES = 'VERTICES'
    SELECTED = 'SELECTED'
    CREDENCIADO = 'CREDENCIADO'
    MANTER = 'MANTER'
    M_INI = 'M_INI'
    P_INI ='P_INI'
    V_INI = 'V_INI'
    DIGITOS = 'DIGITOS'
    SALVAR = 'SALVAR'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.VERTICES,
                self.tr('Camada Vértice'),
                [QgsProcessing.TypeVectorPoint])
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTED,
                self.tr('Apenas selecionados'),
                defaultValue = False
            )
        )

        my_settings = QgsSettings()
        my_user_code = my_settings.value("GeoINCRA/geoincra_user_code", "")
        if my_user_code == "":
            user_code_txt = 'Código do credenciado INCRA'
        else:
            user_code_txt = 'Código do credenciado INCRA ou usar código abaixo'

        self.addParameter(
            QgsProcessingParameterString(
                self.CREDENCIADO,
                user_code_txt,
                defaultValue = my_user_code
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.MANTER,
                self.tr('Manter atributos já preenchidos'),
                defaultValue = True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.M_INI,
                self.tr('Tipo M - primeiro número'),
                type = 0,
                defaultValue = 1,
                minValue = 1
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.P_INI,
                self.tr('Tipo P - primeiro número'),
                type = 0,
                defaultValue = 1,
                minValue = 1
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.V_INI,
                self.tr('Tipo V - primeiro número'),
                type = 0,
                defaultValue = 1,
                minValue = 1
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DIGITOS,
                self.tr('Número de dígitos'),
                type = 0,
                defaultValue = 4,
                minValue = 4
                )
            )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SALVAR,
                self.tr('Salvar Edições'),
                defaultValue = False
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        vertice = self.parameterAsVectorLayer(
            parameters,
            self.VERTICES,
            context
        )
        if vertice is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.VERTICES))

        selecionados = self.parameterAsBool(
            parameters,
            self.SELECTED,
            context
        )

        credenciado = self.parameterAsString(
            parameters,
            self.CREDENCIADO,
            context
        )
        credenciado = credenciado.upper().replace(' ','').replace('-','')

        my_settings = QgsSettings()
        my_settings.setValue("GeoINCRA/geoincra_user_code", parameters[self.CREDENCIADO])

        manter = self.parameterAsBool(
            parameters,
            self.MANTER,
            context
        )

        cont_m = self.parameterAsInt(
            parameters,
            self.M_INI,
            context
        )

        cont_p = self.parameterAsInt(
            parameters,
            self.P_INI,
            context
        )

        cont_v = self.parameterAsInt(
            parameters,
            self.V_INI,
            context
        )

        digitos = self.parameterAsInt(
            parameters,
            self.DIGITOS,
            context
        )
        padrao = '{:0Xd}'.replace('X', str(digitos))

        # Validações

        # Verificação de Modelo de Dados
        field_names = [campo.name() for campo in vertice.fields()]

        for att in ['vertice', 'tipo_verti', 'indice']: # GeoRural
            if att not in field_names:
                tipoModel = 'notGeoRural'
                break
        else:
            tipoModel = 'GeoRural'

        if tipoModel is 'notGeoRural':
            for att in ['type', 'sequence', 'code']: # TopoGeo
                if att not in field_names:
                    tipoModel = 'notTopoGeo'
                    break
            else:
                tipoModel = 'TopoGeo'

        if tipoModel is 'notTopoGeo':
            raise QgsProcessingException('Camada de entrada não está no modelo GeoRural e nem no TopoGeo! Verifique a documentação do plugin!')

        # Atributos
        feedback.pushInfo('Modelo {} identificado...'.format(tipoModel))
        if tipoModel == 'GeoRural':
            att_vertice, att_tipo_verti, att_indice = 'vertice', 'tipo_verti', 'indice'
        else:
            att_vertice, att_tipo_verti, att_indice = 'code', 'type', 'sequence'

        # Tipo vertice
        dic_tipo_vert = {1:'M', 2:'P', 3:'V'}

        # verificar se o campo indice está preenchido corretamente
        indices = []
        for feat in vertice.getSelectedFeatures() if selecionados else vertice.getFeatures():
            ind = feat[att_indice]
            if ind:
                indices += [ind]
            else:
                raise QgsProcessingException('A sequência dos vértices deve ser preenchida para todas as feições!')
        indices.sort()
        if indices[-1] != len(indices):
            raise QgsProcessingException('A sequência dos vértices deve ser preenchida corretamente!')

        # verificar se o campo "tipo de vértice" está preenchido
        for feat in vertice.getSelectedFeatures() if selecionados else vertice.getFeatures():
            tipo = feat[att_tipo_verti]
            if tipo not in ('M', 'P', 'V', 1, 2, 3):
                raise QgsProcessingException('Verifique o preenchimento do campo "tipo de vértice"!')

        # Verificar se o valor "credenciado" é composto apenas por letras (no mínimo 3)
        if len(credenciado) not in (3,4):
            raise QgsProcessingException('O código do credenciado deve ter 3 ou 4 letras!')

        # Listando valores para preenchimento
        dic = {}
        for feat in vertice.getSelectedFeatures() if selecionados else vertice.getFeatures():
            print('oi')
            codigo_vert = feat[att_vertice]
            if tipoModel == 'TopoGeo':
                tipo = dic_tipo_vert[feat[att_tipo_verti]]
            else:
                tipo = feat[att_tipo_verti]
            sequencia = feat[att_indice]
            if codigo_vert:
                if len(codigo_vert) < 8: # preenchido de forma errada
                    dic[sequencia] = tipo
                else: # preenchido corretamente
                    if not manter:
                        dic[sequencia] = tipo
            else:
                dic[sequencia] = tipo

        # Atribuir valores dos códigos para cada ponto na ordem
        ordem = list(dic.keys())
        ordem.sort()
        for k in ordem:
            tipo = dic[k]
            if tipo == 'M':
                dic[k] = credenciado + '-M-' + padrao.format(cont_m)
                cont_m += 1
            elif tipo == 'P':
                dic[k] = credenciado + '-P-' + padrao.format(cont_p)
                cont_p += 1
            elif tipo == 'V':
                dic[k] = credenciado + '-V-' + padrao.format(cont_v)
                cont_v += 1

        # Inserir valores dos códigos dos vértices nas feições
        total = vertice.featureCount()
        columnIndex = vertice.fields().indexFromName(att_vertice)

        vertice.startEditing()

        for k, feat in enumerate(vertice.getSelectedFeatures() if selecionados else vertice.getFeatures()):
            sequencia = feat[att_indice]
            if sequencia in dic:
                codigo_vert = dic[sequencia]
                vertice.changeAttributeValue(feat.id(), columnIndex, codigo_vert)
                feedback.setProgress(int((k+1) * total))
                if feedback.isCanceled():
                    break

        salvar = self.parameterAsBool(
           parameters,
           self.SALVAR,
           context
        )
        if salvar is None:
           raise QgsProcessingException(self.invalidSourceError(parameters, self.SAVE))

        if salvar:
           vertice.commitChanges() # salva as edições

        return {}
