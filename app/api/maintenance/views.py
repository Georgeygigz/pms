import logging
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
import rules
from django_filters.rest_framework import DjangoFilterBackend

from app.api.maintenance.models import MaintenanceRequest, WorkOrder
from app.api.maintenance.serializers import MaintenanceRequestSerializer, WorkOrderSerializer
from app.api.viewmixins import OrganizationScopedMixin
from app.api.maintenance.tasks import send_work_order_notification

logger = logging.getLogger(__name__)


class MaintenanceRequestViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "priority", "property"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return MaintenanceRequest.objects.none()
        org = self.get_organization()
        self.ensure_membership(org)
        qs = MaintenanceRequest.objects.filter(organization=org)
        if self.is_org_admin(org):
            return qs
        return qs.filter(created_by=self.request.user)

    def get_object(self):
        obj = super().get_object()
        if not rules.test_rule("view_maintenance_request", self.request.user, obj):
            raise PermissionDenied("You do not have access to this maintenance request")
        return obj
    

    def perform_create(self, serializer):
        org = self.get_organization()
        self.ensure_membership(org)
        prop = serializer.validated_data["property"]
        if prop.organization_id != org.id:
            raise PermissionDenied("Property does not belong to this organization.")
        serializer.save(organization=org, created_by=self.request.user, updated_by=self.request.user)
    

    def perform_update(self, serializer):
        obj = self.get_object()
        if not rules.test_rule("update_maintenance_request", self.request.user, obj):
            raise PermissionDenied("You can't update this maintenance request")
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        if not rules.test_rule("delete_maintenance_request", self.request.user, self.get_organization()):
            raise PermissionDenied("Only admins can delete maintenance requess")
        instance.delete()
    
    
class WorkOrderViewSet(OrganizationScopedMixin, viewsets.ModelViewSet):
    serializer_class = WorkOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_maintenance_request(self):
        org = self.get_organization()
        self.ensure_membership(org)
        return MaintenanceRequest.objects.get(pk=self.kwargs["mr_pk"], organization=org)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return WorkOrder.objects.none()
        org = self.get_organization()
        self.ensure_membership(org)
        mr = self.get_maintenance_request()
        qs = WorkOrder.objects.filter(maintenance_request=mr, organization=org)
        if self.is_org_admin(org):
            return qs
        return qs.filter(maintenance_request__created_by=self.request.user)

    def get_object(self):
        obj = super().get_object()
        if not rules.test_rule("view_work_orders", self.request.user, obj.maintenance_request):
            raise PermissionDenied("You do not have access to this work order.")
        return obj

    def perform_create(self, serializer):
        org = self.get_organization()
        self.ensure_membership(org)
        if not rules.test_rule("manage_work_orders", self.request.user, org):
            raise PermissionDenied("Only admins can manage work orders.")
        mr = self.get_maintenance_request()
        work_order = serializer.save(organization=org, maintenance_request=mr)
        try:
            send_work_order_notification.delay(str(work_order.id))
        except Exception:
            # we are doing this since this is a background process, and a
            # background process should not break synchronous process
            logger.exception("Failed to enqueue work order notification", extra={"work_order_id": str(work_order.id)})
