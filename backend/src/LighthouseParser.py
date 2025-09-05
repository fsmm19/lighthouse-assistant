import json

class LighthouseParser:
    def __init__(self):
        self.report_data = None

    def parse_report(self, json_string):
        """
        Parsea una cadena JSON que representa un reporte de Lighthouse y almacena el resultado en la instancia

        Args:
            json_string (str): Un string con formato JSON que contiene los datos del reporte Lighthouse
        
        Raises:
            TypeError: Si la entrada no es un string
            ValueError: Si el string de entrada está vacío o no es JSON válido, o si el informe no es un informe Lighthouse válido.
        """
        # Validar que el input sea un string
        if not isinstance(json_string, str):
            raise TypeError("The parameter must be a JSON string")
        
        # Validar que el string no este vacío
        if not json_string.strip():
            raise ValueError("JSON string cannot be empty")
        
        try:
            # Convertir el string a un diccionario Python
            self.report_data = json.loads(json_string)
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
        
        # Validar que es un reporte de Lighthouse
        self.validate_lighthouse_report()
    
    def validate_lighthouse_report(self):
        """
        Valida que el informe Lighthouse cargado tenga la estructura y las categorías requeridas

        Este método comprueba que:
        1. El informe contiene las claves necesarias ('lighthouseVersion', 'categories')
        2. Al menos una de las categorías objetivo ('performance', 'accessibility', 'seo') está presente

        Raises:
            ValueError: Si al informe le faltan claves requeridas o no contiene ninguna de las categorías objetivo
        """
        # Verificar estructura básica de Lighthouse
        required_keys = ['lighthouseVersion', 'categories']

        for key in required_keys:
            if key not in self.report_data:
                raise ValueError(f"Not a valid Lighthouse report: missing '{key}'")
        
        # Verificar que existe al menos una de las categorías de interes
        categories = self.report_data.get('categories', {})
        target_categories = ['performance', 'accessibility', 'seo']
        available_categories = []

        for category in target_categories:
            if category in categories:
                available_categories.append(category)
        
        if not available_categories:
            raise ValueError(f"The report does not contain any of the required categories: {', '.join(target_categories)}")
        
        # Informar que categorías están disponibles
        missing_categories = [category for category in target_categories if category not in available_categories]

        # Si se llega aquí, el reporte es válido
        print(f"✓ Lighthouse v{self.report_data['lighthouseVersion']} report successfully uploaded")
        print(f"✓ Categories available: {', '.join(available_categories)}")

        if missing_categories:
            print(f"⚠ Categories not available: {', '.join(missing_categories)}")