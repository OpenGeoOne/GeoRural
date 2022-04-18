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
__date__ = '2022-02-13'
__copyright__ = '(C) 2022 by Tiago Prudencio e Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingParameterField,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsFeature,
                       QgsProject,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer)
from qgis import processing
from qgis.PyQt.QtGui import QIcon
from GeoINCRA.images.Imgs import *
import os


class addFeat(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return addFeat()

    def name(self):
        return 'addFeat'

    def displayName(self):
        return self.tr('Alimentar camada vértice')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/geoincra_pb.png'))

    def shortHelpString(self):
        txt = 'Esta ferramenta carrega as feições selecionadas de uma camada de pontos para dentro da camada vértices do banco de dados GeoRural.'

        footer = '''<div>
                      <div align="center">
                      <img style="width: 100%; height: auto;" src="data:image/jpg;base64,'''+ INCRA_GeoOne +'''
                      </div>
                      <div align="right">
                      <p align="right">
                      <a href="https://github.com/OpenGeoOne/GeoINCRA/wiki/Sobre-o-GeoINCRA"><span style="font-weight: bold;">Clique aqui para conhecer o modelo GeoRural da GeoOne</span></a><br>
                      </p>
                      <a target="_blank" rel="noopener noreferrer" href="https://geoone.com.br/"><img title="GeoOne" src="data:image/png;base64,'''+ GeoOne +'''"></a>
                      <p><i>"Mapeamento automatizado, fácil e direto ao ponto é na GeoOne"</i></p>
                      </div>
                    </div>'''
        return txt + footer

    sigma_x = 'sigma_x'
    sigma_y = 'sigma_y'
    sigma_z = 'sigma_z'
    metodo_pos = 'metodo_pos'
    vertice = 'vertice'
    tipo_verti = 'tipo_verti'
    qrcode = 'qrcode'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Camada de pontos a serem carregados'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.OUTPUT,
                self.tr('Camada de vértices do banco de dados GeoRural'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.sigma_x,
                self.tr('Precisão em X'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.sigma_y,
                self.tr('Precisão em Y'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.sigma_z,
                self.tr('Precisão em Z'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.metodo_pos,
                self.tr('Método de posicionamento'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.vertice,
                self.tr('Código do vértice'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.tipo_verti,
                self.tr('Tipo de Vértice (M,P ou V)'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.qrcode,
                self.tr('qrcode'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        source_in = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if not source_in:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        #if source_in.sourceCrs() != QgsCoordinateReferenceSystem('EPSG:4674'):
            #raise QgsProcessingException('A camada de entrada deve estar em SIRGAS 2000 (EPSG:4674)!')

        sigma_x = self.parameterAsFields(parameters, self.sigma_x, context)
        if sigma_x:
            sigma_x = sigma_x[0]
        sigma_y = self.parameterAsFields(parameters, self.sigma_y, context)
        if sigma_y:
            sigma_y = sigma_y[0]
        sigma_z = self.parameterAsFields(parameters, self.sigma_z, context)
        if sigma_z:
            sigma_z = sigma_z[0]
        metodo_pos = self.parameterAsFields(parameters, self.metodo_pos, context)
        if metodo_pos:
            metodo_pos = metodo_pos[0]
        vertice = self.parameterAsFields(parameters, self.vertice, context)
        if vertice:
            vertice = vertice[0]
        tipo_verti = self.parameterAsFields(parameters, self.tipo_verti, context)
        if tipo_verti:
            tipo_verti = tipo_verti[0]
        qrcode = self.parameterAsFields(parameters, self.qrcode, context)
        if qrcode:
            qrcode = qrcode[0]

        source_out = self.parameterAsVectorLayer(
            parameters,
            self.OUTPUT,
            context
        )
        if not source_out:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.OUTPUT))

        total = 100.0 / source_in.featureCount() if source_in.featureCount() else 0

        for current, feature in enumerate(source_in.getFeatures()):
            feat = QgsFeature(source_out.fields())
            if sigma_x:
                feat.setAttribute('sigma_x', float(feature[sigma_x].replace(',','.')) if isinstance(feature[sigma_x], str) else feature[sigma_x])
            if sigma_y:
                feat.setAttribute('sigma_y', float(feature[sigma_y].replace(',','.')) if isinstance(feature[sigma_y], str) else feature[sigma_y])
            if sigma_z:
                feat.setAttribute('sigma_z', float(feature[sigma_z].replace(',','.')) if isinstance(feature[sigma_z], str) else feature[sigma_z])
            if metodo_pos:
                feat.setAttribute('metodo_pos',feature[metodo_pos])
            if vertice:
                feat.setAttribute('vertice',feature[vertice])
            if tipo_verti:
                feat.setAttribute('tipo_verti',feature[tipo_verti])
            if qrcode:
                feat.setAttribute('qrcode',feature[qrcode])

            crsSrc = QgsCoordinateReferenceSystem(source_in.sourceCrs())
            crsDest = QgsCoordinateReferenceSystem('EPSG:4674')
            proj2geo = QgsCoordinateTransform(crsSrc, crsDest,QgsProject.instance())
            geom = feature.geometry()
            geom.transform(proj2geo)

            feat.setGeometry(geom) # VERIFICAR SE AS CAMADAS ESTÃO NO MESMO SRC!!!!
            (res, outFeats) = source_out.dataProvider().addFeatures([feat])
            feedback.setProgress(int(current * total))



        return {}
