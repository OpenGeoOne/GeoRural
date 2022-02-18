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

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProject,
                       QgsFeatureRequest,
                       QgsVectorLayer,
                       QgsProcessingParameterExtent,
                       QgsRectangle,
                       QgsProcessingParameterEnum,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

import os


class ConnectBase(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    EXTENT = 'EXTENT'
    WFS = 'WFS'

    mapping ={ 0: 'imóveis Certificados Sigeb - Particular',
               1: 'imóveis Certificados Sigeb - Público',
               2: 'imóveis Certificados SNCI - Privado',
               3: 'imóveis Certificados SNCI - Público',
               4: 'Assentamentos',
               5:'Quilombolas'
            }

    layer_name ={    0: 'ms:certificada_sigef_particular_xx',
               1: 'ms:certificada_sigef_publico_xx',
               2: 'ms:imoveiscertificados_privado_xx',
               3: 'ms:imoveiscertificados_publico_xx',
               4: 'ms:assentamentos_xx',
               5:'ms:quilombolas_xx'
            }

    links = {     'imóveis Certificados Sigeb - Particular': 'http://acervofundiario.incra.gov.br/i3geo/ogc.php?tema=certificada_sigef_particular_xx',
                  'imóveis Certificados Sigeb - Público': 'http://acervofundiario.incra.gov.br/i3geo/ogc.php?tema=certificada_sigef_publico_xx',
                  'imóveis Certificados SNCI - Privado': 'http://acervofundiario.incra.gov.br/i3geo/ogc.php?tema=imoveiscertificados_privado_xx',
                  'imóveis Certificados SNCI - Público': 'http://acervofundiario.incra.gov.br/i3geo/ogc.php?tema=imoveiscertificados_publico_xx',
                  'Assentamentos':'http://acervofundiario.incra.gov.br/i3geo/ogc.php?tema=assentamentos_xx',
                  'Quilombolas':'http://acervofundiario.incra.gov.br/i3geo/ogc.php?tema=quilombolas_xx'
            }

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                self.tr('Extent')
            )
        )



        self.addParameter(
            QgsProcessingParameterEnum(
                self.WFS,
                self.tr('Tipo de Camada'),
                options = self.links.keys(),
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Camada')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        extensao = self.parameterAsExtent(
        parameters,
        self.EXTENT,
        context
        )
        if not extensao:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.EXTENT))

        option = self.parameterAsEnum(parameters, self.WFS, context)
        layer = self.mapping[option]
        name = self.layer_name[option]
        link = self.links[layer]

        path = os.path.dirname(__file__) + "/shp" + "/BR_UF_2020.shp"
        estado = QgsVectorLayer(path, "Brasil", "ogr")


        uris = list()
        for feat in estado.getFeatures():
             if feat.geometry().intersects(extensao):
                 #uri_default="""pagingEnabled='true' preferCoordinatesForWfsT11='false' restrictToRequestBBOX='1' srsname='EPSG:4326' typename='ms:certificada_sigef_particular_xx' url='http://acervofundiario.incra.gov.br/i3geo/ogc.php?tema=certificada_sigef_particular_xx' version='auto'"""
                 uri_default="""pagingEnabled='true' preferCoordinatesForWfsT11='false' restrictToRequestBBOX='1'  srsname='EPSG:4326' typename='name_' url='link' version='auto'"""
                 uri_default = uri_default.replace('name_',name)
                 uri_default = uri_default.replace('link',link)
                 uri_default = uri_default.replace('xx',feat['SIGLA_UF'])
                 uris.append(uri_default)

        source = QgsVectorLayer(uris[0], "my wfs layer", "WFS")
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        for uri in uris:
            vlayer = QgsVectorLayer(uri, "my wfs layer", "WFS")

            request = QgsFeatureRequest().setFilterRect(extensao)

            for current, feature in enumerate(vlayer.getFeatures(request)):
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    break

                # Add a feature in the sink
                sink.addFeature(feature, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'connectbase'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Conecta Base INCRA')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConnectBase()

    def shortHelpString(self):

        return self.tr("Conecta a base de dados do INCRA para baixar os dados em formato shapefile (*.shp) de uma área selecionada pelo usuário.")
