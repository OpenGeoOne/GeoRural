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
__date__ = '2022-05-08'
__copyright__ = '(C) 2022 by Tiago Prudencio e Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterBoolean,
                       QgsFeature,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer)

from qgis.PyQt.QtGui import QIcon
from GeoINCRA.images.Imgs import *
import os


class ToTopoGeo(QgsProcessingAlgorithm):

    def tr(self, string):

        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ToTopoGeo()

    def name(self):

        return 'totopogeo'

    def displayName(self):

        return self.tr('GeoRural para TopoGeo')

    def group(self):

        return self.tr(self.groupId())

    def groupId(self):

        return ''

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/geoincra_pb.png'))

    def shortHelpString(self):
        txt = '''Esta ferramenta copia as feições das camadas "vértices", "limites" e "parcela" do banco de dados <b>GeoRural</b> para as camdas "ponto limite", "elemento confrontante" e "área do imóvel" do banco <b>TopoGeo</b>, aproveitando-se os atributos em comum.
        Com a feições no modelo TopoGeo, é possível gerar o Memorial Descritivo e Planta Topográfica automaticamente.'''

        footer = '''<div>
                      <div align="center">
                      <img style="width: 100%; height: auto;" src="data:image/jpg;base64,'''+ INCRA_GeoOne +'''
                      </div>
                      <div align="right">
                      <p align="right">
                      <a href="https://geoone.com.br/ebooks/ebook_gratis/"><span style="font-weight: bold;">Clique aqui para conhecer o modelo <b>TopoGeo</b></span></a><br>
                      </p>
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

    PONTOS_INI = 'PONTOS_INI'
    PONTOS_FIM = 'PONTOS_FIM'
    LINHAS_INI = 'LINHAS_INI'
    LINHAS_FIM = 'LINHAS_FIM'
    AREA_INI = 'AREA_INI'
    AREA_FIM = 'AREA_FIM'
    SALVAR = 'SALVAR'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.PONTOS_INI,
                self.tr('Camada Vértice (GeoRural)'),
                [QgsProcessing.TypeVectorPoint],
                optional = True
                )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.PONTOS_FIM,
                self.tr('Pontos Limite (TopoGeo)'),
                [QgsProcessing.TypeVectorPoint],
                optional = True
            )
        )

        self.addParameter(
			QgsProcessingParameterFeatureSource(
				self.LINHAS_INI,
				self.tr('Camada Limite (GeoRural)'),
				[QgsProcessing.TypeVectorLine],
                optional = True
			)
		)

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LINHAS_FIM,
                self.tr('Elemento Confrontante (TopoGeo)'),
                [QgsProcessing.TypeVectorLine],
                optional = True
            )
        )

        self.addParameter(
			QgsProcessingParameterFeatureSource(
				self.AREA_INI,
				self.tr('Camada Parcela (GeoRural)'),
				[QgsProcessing.TypeVectorPolygon],
                optional = True
			)
		)

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.AREA_FIM,
                self.tr('Área do imóvel (TopoGeo)'),
                [QgsProcessing.TypeVectorPolygon],
                optional = True
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

        origem1 = self.parameterAsSource(
            parameters,
            self.PONTOS_INI,
            context
        )

        dest1 = self.parameterAsVectorLayer(
            parameters,
            self.PONTOS_FIM,
            context)

        origem2 = self.parameterAsSource(
            parameters,
            self.LINHAS_INI,
            context
        )

        dest2 = self.parameterAsVectorLayer(
            parameters,
            self.LINHAS_FIM,
            context)

        origem3 = self.parameterAsSource(
            parameters,
            self.AREA_INI,
            context
        )

        dest3 = self.parameterAsVectorLayer(
            parameters,
            self.AREA_FIM,
            context)


        #Vértice > limit_point_p
        dic_1 = {
        'type':['tipo_verti' , {'M':1, 'P':2, 'V':3}],
        'code': 'vertice',
        'sequence': 'indice'
        }

        #Limite > boundary_element_l
        dic_2 = {
        'borderer': 'confrontan',
        'borderer_registry': 'matricula'
        }

        #Parcela > property_area_a
        dic_3 = {
        'property': 'denominacao',
        'registry': 'sncr',
        'transcript': 'matricula',
        'owner': 'nome',
        'county': 'municipio',
        'state': 'uf',
        'survey_date': 'data',
        'tech_manager':'resp_tec',
        'prof_id':'reg_prof'
        }

        # Conversão
        conversoes = []
        total_feicoes = 0
        if origem1 and dest1:
            conversoes += [[origem1, dest1, dic_1]]
            total_feicoes += origem1.featureCount()
        if origem2 and dest2:
            conversoes += [[origem2, dest2, dic_2]]
            total_feicoes += origem2.featureCount()
        if origem3 and dest3:
            conversoes += [[origem3, dest3, dic_3]]
            total_feicoes += origem3.featureCount()

        total = 100.0 / total_feicoes if total_feicoes else 0
        cont = 0

        for conv in conversoes:
            origem = conv[0]
            dest = conv[1]
            feedback.pushInfo('Copiando feições da camada {} para a camada {}...'.format(origem.sourceName(), dest.sourceName()))
            dic_transf = conv[2]
            dest.startEditing()
            feature = QgsFeature(dest.fields())
            for feat in origem.getFeatures():
                for item in dic_transf:
                    try:
                        if isinstance( dic_transf[item], list):
                            campo = dic_transf[item][0]
                            dic = dic_transf[item][1]
                            feature[item] = dic[feat[campo]]
                        else:
                            feature[item] = feat[dic_transf[item]]
                    except:
                        pass
                feature.setGeometry(feat.geometry())
                dest.addFeatures([feature])
                cont += 1
                feedback.setProgress(int(cont * total))
                if feedback.isCanceled():
                    break

        salvar = self.parameterAsBool(
            parameters,
            self.SALVAR,
            context
        )
        if salvar is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SALVAR))

        if salvar:
            dest1.commitChanges()
            dest2.commitChanges()
            dest3.commitChanges()

        return {}
