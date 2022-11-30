def classFactory(iface):
    """Load GeoQuiz class from file GeoQuiz.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .geo_quiz import GeoQuiz

    return GeoQuiz(iface)
