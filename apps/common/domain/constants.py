from dataclasses import dataclass


class VehicleType:
    MOTO = 'MOTO'
    LIVIANO = 'LIVIANO'
    PESADO = 'PESADO'

    ALL = (MOTO, LIVIANO, PESADO)


class InspectionStatus:
    BORRADOR = 'BORRADOR'
    EN_PROGRESO = 'EN_PROGRESO'
    CERRADA = 'CERRADA'

    ALL = (BORRADOR, EN_PROGRESO, CERRADA)


class GeneralResult:
    APROBADO = 'APROBADO'
    RECHAZADO = 'RECHAZADO'

    ALL = (APROBADO, RECHAZADO)


class DefectType:
    A = 'A'
    B = 'B'

    ALL = (A, B)


@dataclass(frozen=True)
class TemplateCode:
    MOTOS: str = 'MOTOS'
    LIVIANOS_PESADOS: str = 'LIVIANOS_PESADOS'
