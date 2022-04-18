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

from qgis.PyQt.QtCore import QCoreApplication,QVariant
from qgis.core import (QgsProcessing,
					   QgsFeatureSink,
					   QgsProcessingException,
					   QgsFeature,
					   QgsField,
					   QgsGeometry,
					   QgsVectorLayer,
					   QgsProcessingParameterFeatureSource,
					   QgsProcessingAlgorithm,
					   QgsProcessingParameterFile,
					   QgsProcessingParameterFileDestination)
from qgis import processing
import pandas as pd
from qgis.PyQt.QtGui import QIcon
from GeoINCRA.images.Imgs import *
import os


class createTemplate(QgsProcessingAlgorithm):

	VERTICE = 'VERTICE'
	LIMITE  = 'LIMITE'
	PARCELA  ='PARCELA'
	OUTPUT = 'OUTPUT'

	def tr(self, string):
		return QCoreApplication.translate('Processing', string)

	def createInstance(self):
		return createTemplate()

	def name(self):
		return 'createtemplate'

	def displayName(self):
		return self.tr('Gerar TXT para Planilha ODS')

	def group(self):
		return self.tr(self.groupId())

	def groupId(self):
		return ''

	def icon(self):
		return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/geoincra_pb.png'))

	def shortHelpString(self):
		txt = "Cria um arquivo de Texto (TXT) com todas os dados necessários para preencher a planilha ODS do SIGEF."

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

	def initAlgorithm(self, config=None):

		self.addParameter(
			QgsProcessingParameterFeatureSource(
				self.VERTICE,
				self.tr('Camada Vertice'),
				[QgsProcessing.TypeVectorPoint]
			)
		)

		self.addParameter(
			QgsProcessingParameterFeatureSource(
				self.LIMITE,
				self.tr('Camada Limite'),
				[QgsProcessing.TypeVectorLine]
			)
		)

		self.addParameter(
			QgsProcessingParameterFeatureSource(
				self.PARCELA,
				self.tr('Camada Parcela'),
				[QgsProcessing.TypeVectorPolygon]
			)
		)

		self.addParameter(
			QgsProcessingParameterFileDestination(
				self.OUTPUT,
				self.tr('TXT de dados da Planilha ODS'),
				self.tr('Texto (*.txt)')
			)
		)

	def processAlgorithm(self, parameters, context, feedback):

		vertice = self.parameterAsVectorLayer(
			parameters,
			self.VERTICE,
			context
		)

		if vertice is None:
			raise QgsProcessingException(self.invalidSourceError(parameters, self.VERTICE))

		for feature in vertice.getFeatures():
			if not feature['Ordem do vértice']:
				raise QgsProcessingException('ERRO: O vertice (id = {}) , atributo Ordem do Vértice é de PREENCHIMENTO OBRIGATÓRIO'.format(feature.id()))

			elif not feature['Código do Vértice']:
				raise QgsProcessingException('ERRO: O vertice (id = {}) , atributo Código do Vértice é de PREENCHIMENTO OBRIGATÓRIO'.format(feature.id()))

			elif not feature['Método de Posicionamento']:
				raise QgsProcessingException('ERRO: O vertice (id = {}) , atributo Método de Posicionamento é de PREENCHIMENTO OBRIGATÓRIO'.format(feature.id()))




		self.limite = self.parameterAsVectorLayer(
			parameters,
			self.LIMITE,
			context
		)

		if self.limite is None:
			raise QgsProcessingException(self.invalidSourceError(parameters, self.LIMITE))

		self.parcela = self.parameterAsVectorLayer(
			parameters,
			self.PARCELA,
			context
		)

		if self.parcela is None:
			raise QgsProcessingException(self.invalidSourceError(parameters, self.PARCELA))


		output_path = self.parameterAsString(
			parameters,
			self.OUTPUT,
			context
		)
		if not output_path:
			raise QgsProcessingException(self.invalidSourceError(parameters, self.OUTPUT))

		arq =  open(output_path,'w')
		self.writeHead(arq)

		field= QgsField( 'long', QVariant.String)
		vertice.addExpressionField('''to_dms($x ,'x',3,'suffix')''', field)
		field= QgsField( 'lat', QVariant.String)
		vertice.addExpressionField('''to_dms($y ,'y',3, 'suffix')''',field)

		parc = [parcela.geometry() for parcela in self.parcela.getFeatures()][0]

		ordena = dict()
		for feature in vertice.getFeatures():
			ordena[feature['Ordem do Vértice']] = feature
		vertices = [ordena[key] for key in sorted(ordena.keys())]

		point_out = list()

		for count, part in enumerate(parc.parts()):
			geom = QgsGeometry.fromWkt(part.asWkt())
			arq.write('Parcela ' + str(count+1)+ '\n')
			linhas = list()

			for feat in vertices:
				if feat.geometry().intersection(geom):
					linha = list()
					linha.append(feat['vertice'])
					linha.append(self.fixCoord(feat['long']))
					linha.append(self.fixSigma(feat['sigma_x']))
					linha.append(self.fixCoord(feat['lat']))
					linha.append(self.fixSigma(feat['sigma_y']))
					linha.append(self.getZ(feat))
					linha.append(self.fixSigma(feat['sigma_z']))
					linha.append(feat['metodo_pos'])
					att = self.getAtt(feat,feedback)
					if not att:
						vertice.removeExpressionField(vertice.fields().indexOf('long'))
						vertice.removeExpressionField(vertice.fields().indexOf('lat'))
						raise QgsProcessingException('ERRO: O ponto {} não intercepta a camada limite'.format(feat['Código do Vértice']))
						arq.write('\nERRO: O ponto {} não intercepta a camada limite\n'.format(feat['Código do Vértice']))
						break
					linha.append(att['tipo'])
					linha.append(att['cns'])
					linha.append(att['matricula'])
					linha.append(att['Confrontante'])
					linha = self.listaExchange(linha)
					linhas.append(linha)
				else:
					point_out.append(feat)


			head_line = ['vertice','long', 'sigma_x','lat', 'sigma_y','h', 'sigma_z','metodo_pos','tipo_limite','cns','Matrícula','Descritivo']
			df = pd.DataFrame(linhas, columns = head_line)
			df = df.to_csv(sep = '\t',header=None, index=False).strip('\n').split('\n')
			df_string = ''.join(df)
			arq.writelines(df_string)
			arq.write('\n\n')

		for feat in point_out:
			#feedback.pushInfo('ERRO: O ponto {} não intercepta a camada parcela'.format(feat['Código do Vértice']))
			raise QgsProcessingException('ERRO: O ponto {} não intercepta a camada parcela'.format(feat['Código do Vértice']))
			arq.write('\nERRO: O ponto {} não intercepta a camada parcela\n'.format(feat['Código do Vértice']))

		vertice.removeExpressionField(vertice.fields().indexOf('long'))
		vertice.removeExpressionField(vertice.fields().indexOf('lat'))
		arq.close

		return {}

	def fixCoord(self, coord):
		coord = coord.replace('°',' ')
		coord = coord.replace('′',' ')
		coord = coord.replace('″',' ')
		coord = coord.replace('.',',')

		return (coord)

	def fixSigma(self, sigma):
		sigma = "{0:.2f}".format(round(sigma,2))
		sigma = str(sigma).replace('.',',')
		return(sigma)


	def getZ(self,feat):
		try:
			coord = str(feat.geometry().constGet().z()).replace('.',',')
			return coord
		except:
			return '0'

	def getAtt (self,feat,feedback):
		att = dict()
		for feature in self.limite.getFeatures():
			if feature.geometry().asPolyline()[0] == feat.geometry().asPoint():
				att['tipo'] =  feature['tipo']
				att['cns'] = feature['cns']
				att['matricula'] = feature['matricula']
				att['Confrontante'] = feature['Confrontante']
				break
			elif feat.geometry().asPoint() in feature.geometry().asPolyline():
				att['tipo'] =  feature['tipo']
				att['cns'] = feature['cns']
				att['matricula'] = feature['matricula']
				att['Confrontante'] = feature['Confrontante']


		try:
			return (att)
		except:
			#feedback.pushInfo('ERRO: O ponto {} não intercepta a camada limite'.format(feat['Código do Vértice']))
			return ()

	def listaExchange(self,strings):
		new_strings  = list()
		for string in strings:
			new_string = str(string).replace("NULL", "")
			new_strings.append(new_string)
		return new_strings

	def writeHead(self,arq):
		nat_ser = {1:'Particular', 2:'Contrato com Adm Pública'}

		pessoa = {1:'Física', 2:'Jurídica'}

		for feat in self.parcela.getFeatures():
			arq.write('Natureza do Serviço:'+ nat_ser[feat['nat_serv']]+ '\n')
			arq.write('Tipo Pessoa:'+ pessoa[feat['pessoa']]+ '\n')
			arq.write('nome:'+ str(feat['nome'])+ '\n')
			arq.write('cpf:'+ str(feat['cpf_cnpj'])+ '\n')
			arq.write('denominação:'+ str(feat['denominacao'])+ '\n')
			arq.write('situação:'+ str(feat['situacao'])+ '\n')
			arq.write('Código do Imóvel (SNCR/INCRA):'+ str(feat['sncr'])+ '\n')
			arq.write('Código do cartório (CNS):'+ str(feat['cod_cartorio'])+ '\n')
			arq.write('Matricula:'+ str(feat['matricula'])+ '\n')
			arq.write('Município:'+ str(feat['municipio'])+ '\n')
			arq.write('UF:'+ str(feat['uf'])+ '\n')
			arq.write('\n\n')
