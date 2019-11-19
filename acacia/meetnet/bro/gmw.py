from xml.etree.ElementTree import Element, SubElement
from .models import MapSheet
    
def registration_request(well, kvk):
    ''' Creates xml with registration request (registratieverzoek) for BRO '''
    # TODO: handle missing data, e.g. screen settings, reference point or surface level
    request = Element('ns:registrationRequest',
    {
        'xmlns:ns':'http://www.broservices.nl/xsd/isgmw/1.1',
        'xmlns:ns1':'http://www.broservices.nl/xsd/brocommon/3.0',        
        'xmlns:ns2':'http://www.broservices.nl/xsd/gmwcommon/1.1',
        'xmlns:ns3':'http://www.opengis.net/gml/3.2'
    })
    SubElement(request, 'ns1:requestReference').text = 'BRO registratieverzoek voor put {}'.format(well)
    SubElement(request, 'ns1:deliveryAccountableParty').text = kvk
    SubElement(request, 'ns1:qualityRegime').text = 'IMBRO/A'
    
    sourceDocument = SubElement(request, 'ns:sourceDocument')
    construction = SubElement(sourceDocument, 'ns:GMW_Construction')

    SubElement(construction, 'ns:objectIdAccountableParty').text = well.name 
    SubElement(construction, 'ns:deliveryContext', codeSpace='urn:bro:gmw:DeliveryContext').text = 'publiekeTaak'
    SubElement(construction, 'ns:constructionStandard', codeSpace='urn:bro:gmw:ConstructionStandard').text = 'onbekend'
    SubElement(construction, 'ns:initialFunction', codeSpace='urn:bro:gmw:InitialFunction').text = 'stand'
    SubElement(construction, 'ns:numberOfMonitoringTubes').text = str(well.screen_set.count())
    SubElement(construction, 'ns:groundLevelStable').text = 'onbekend'
    SubElement(construction, 'ns:wellStability', codeSpace='urn:bro:gmw:WellStability').text = 'onbekend'
    if well.nitg:
        SubElement(construction, 'ns:nitgCode').text = well.nitg
    else:
        sheets = MapSheet.from_location(well.location)
        if sheets.exists():
            SubElement(construction, 'ns:mapSheetCode').text = sheets.first().blad 
        else:
            raise Exception('Could not determine mapSheetCode for well "{}"'.format(well.name))

    SubElement(construction, 'ns:owner').text = kvk
    SubElement(construction, 'ns:maintenanceResponsibleParty').text = kvk
    SubElement(construction, 'ns:wellHeadProtector', codeSpace='urn:bro:gmw:WellHeadProtector').text = 'pot'
    
    constructionDate = SubElement(construction, 'ns:wellConstructionDate')
    SubElement(constructionDate, 'ns1:date').text = str(well.date)
    deliveredLocation = SubElement(construction, 'ns:deliveredLocation')
    location = SubElement(deliveredLocation, 'ns2:location', {'ns3:id': 'id-426a1f26-360b-45e8-8c9d-469e6b33c7c3', 'srsName': 'urn:ogc:def:crs:EPSG::28992'})
    pos = well.RD()
    SubElement(location, 'ns3:pos').text = '{:.2f} {:.2f}'.format(pos.x, pos.y)
    SubElement(deliveredLocation, 'ns2:horizontalPositioningMethod', codeSpace='urn:bro:gmw:HorizontalPositioningMethod').text = 'GPSOnbekend'
    deliveredVerticalPosition = SubElement(construction, 'ns:deliveredVerticalPosition') 
    SubElement(deliveredVerticalPosition, 'ns2:localVerticalReferencePoint', codeSpace='urn:bro:gmw:LocalVerticalReferencePoint').text = 'NAP'
    SubElement(deliveredVerticalPosition, 'ns2:offset', uom='m').text = '0.00'
    SubElement(deliveredVerticalPosition, 'ns2:verticalDatum', codeSpace='urn:bro:gmw:VerticalDatum').text = 'NAP'
    SubElement(deliveredVerticalPosition, 'ns2:groundLevelPosition', uom="m").text = '{:.2f}'.format(well.maaiveld)
    SubElement(deliveredVerticalPosition, 'ns2:groundLevelPositioningMethod', codeSpace='urn:bro:gmw:GroundLevelPositioningMethod').text = 'waterpassing2tot4cm'
    
    for screen in well.screen_set.order_by('nr'):
        monitoringTube = SubElement(construction, 'ns:monitoringTube')
        SubElement(monitoringTube, 'ns:tubeNumber').text = str(screen.nr)
        SubElement(monitoringTube, 'ns:tubeType', codeSpace="urn:bro:gmw:TubeType").text='standaardbuis'
        SubElement(monitoringTube, 'ns:artesianWellCapPresent').text = 'nee'
        SubElement(monitoringTube, 'ns:sedimentSumpPresent').text='nee'
        SubElement(monitoringTube, 'ns:numberOfGeoOhmCables').text = '0'
        SubElement(monitoringTube, 'ns:tubeTopDiameter', uom="mm").text = '{}'.format(screen.diameter)
        SubElement(monitoringTube, 'ns:variableDiameter').text='nee'
        SubElement(monitoringTube, 'ns:tubeStatus', codeSpace="urn:bro:gmw:TubeStatus").text='gebruiksklaar'
        SubElement(monitoringTube, 'ns:tubeTopPosition', uom="m").text = '{:.2f}'.format(screen.refpnt)
        SubElement(monitoringTube, 'ns:tubeTopPositioningMethod', codeSpace="urn:bro:gmw:TubeTopPositioningMethod").text = 'waterpassing2tot4cm'
        materialsUsed = SubElement(monitoringTube, 'ns:materialUsed')
        SubElement(materialsUsed,'ns2:tubePackingMaterial', codeSpace="urn:bro:gmw:TubePackingMaterial").text='bentonietFiltergrind'
        SubElement(materialsUsed,'ns2:tubeMaterial',codeSpace="urn:bro:gmw:TubeMaterial").text='pvc'
        SubElement(materialsUsed,'ns2:glue', codeSpace="urn:bro:gmw:Glue").text = 'geen' 
        screenElement = SubElement(monitoringTube, 'ns:screen')
        SubElement(screenElement,'ns:screenLength', uom="m").text = '{:.2f}'.format(screen.top - screen.bottom)
        SubElement(screenElement,'ns:sockMaterial', codeSpace="urn:bro:gmw:SockMaterial").text='nylon'
        plainTubePart = SubElement(monitoringTube, 'ns:plainTubePart')
        SubElement(plainTubePart, 'ns2:plainTubePartLength', uom="m").text = '{:.2f}'.format(screen.top + screen.refpnt - well.maaiveld)

    return request
    
    
