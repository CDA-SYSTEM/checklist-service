from apps.common.domain.exceptions import NotFoundError
from apps.inspections.infrastructure.documents import Inspection, LabradoMeasurement


class InspectionRepository:
    def list_all(self):
        return Inspection.objects.order_by('-inspection_datetime')

    def get_by_id(self, inspection_id: str):
        inspection = Inspection.objects(id=inspection_id).first()
        if not inspection:
            raise NotFoundError('Inspeccion no encontrada.')
        return inspection

    def create(self, payload: dict):
        inspection = Inspection(**payload)
        inspection.save()
        return inspection

    def update(self, inspection_id: str, payload: dict):
        inspection = self.get_by_id(inspection_id)
        for key, value in payload.items():
            if key == 'labrado' and isinstance(value, dict):
                value = LabradoMeasurement(**value)
            setattr(inspection, key, value)
        inspection.save()
        return inspection

    def delete(self, inspection_id: str):
        inspection = self.get_by_id(inspection_id)
        inspection.delete()

    def by_plate(self, plate: str):
        return Inspection.objects(plate__iexact=plate).order_by('-inspection_datetime')

    def by_status(self, status: str):
        return Inspection.objects(status=status).order_by('-inspection_datetime')

    def by_vehicle_id(self, vehicle_id: str):
        return Inspection.objects(vehicle_id=vehicle_id).order_by('-inspection_datetime')

    def by_date_range(self, start_date, end_date):
        return Inspection.objects(inspection_datetime__gte=start_date, inspection_datetime__lte=end_date).order_by(
            '-inspection_datetime'
        )
