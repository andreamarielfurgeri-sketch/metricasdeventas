"""
Módulo de utilidades para el dashboard de ventas
Contiene herramientas de validación y procesamiento de datos
"""

from .validador_datos import (
    ValidadorDatos,
    validar_y_preparar_datos,
    validar_y_preparar_datos_cache
)

__all__ = [
    'ValidadorDatos',
    'validar_y_preparar_datos',
    'validar_y_preparar_datos_cache'
]
