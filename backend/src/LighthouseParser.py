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
            ValueError: Si el string de entrada no es JSON válido
        """

        self._validate_input(json_string)
        
        try:
            self.report_data = json.loads(json_string)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON: {str(error)}")
        
        self._validate_lighthouse_report()
    
    def _validate_input(self, json_string):
        """
        Valida la cadena JSON de entrada
        
        Args:
            json_string (str): La cadena JSON a validar
        Raises:
            TypeError: Si la entrada no es una cadena
            ValueError: Si la cadena de entrada está vacía o sólo contiene espacios en blanco
        """
        if not isinstance(json_string, str):
            raise TypeError("The parameter must be a JSON string")
        
        if not json_string.strip():
            raise ValueError("JSON string cannot be empty")
    
    def _validate_lighthouse_report(self):
        """
        Valida que el informe Lighthouse cargado tenga la estructura y las categorías requeridas

        Este método comprueba que:
        1. El informe contiene las claves necesarias ('lighthouseVersion', 'categories')
        2. Al menos una de las categorías objetivo ('performance', 'accessibility', 'seo') está presente

        Raises:
            ValueError: Si al informe le faltan claves requeridas o no contiene ninguna de las categorías objetivo
        """
        self._check_required_keys()
        available_categories, missing_categories = self._check_categories()

        # Si se llega aquí, el reporte es válido
        print(f"✓ Lighthouse v{self.report_data['lighthouseVersion']} report successfully uploaded")
        print(f"✓ Categories available: {', '.join(available_categories)}")

        if missing_categories:
            print(f"⚠ Categories not available: {', '.join(missing_categories)}")

    def _check_required_keys(self):
        """
        Verifica que el informe contenga las claves estructurales necesarias.
        
        Raises:
            ValueError: Si falta alguna clave requerida en el informe
        """
        required_keys = ['lighthouseVersion', 'categories']

        for key in required_keys:
            if key not in self.report_data:
                raise ValueError(f"Not a valid Lighthouse report: missing '{key}'")

    def _check_categories(self):
        """
        Verifica la presencia de categorías de interés en el informe.
        
        Returns:
            tuple: (available_categories, missing_categories)
            
        Raises:
            ValueError: Si no se encuentra ninguna categoría de interés
        """
        categories = self.report_data.get('categories', {})
        target_categories = ['performance', 'accessibility', 'seo']
        available_categories = []

        for category in target_categories:
            if category in categories:
                available_categories.append(category)
        
        if not available_categories:
            raise ValueError(f"The report does not contain any of the required categories: {', '.join(target_categories)}")
        
        missing_categories = [category for category in target_categories if category not in available_categories]

        return available_categories, missing_categories