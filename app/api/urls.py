
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from app.api.organization.views import OrganizationViewSet, PropertyViewSet
from app.api.maintenance.views import MaintenanceRequestViewSet, WorkOrderViewSet

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organizations")

org_router = NestedSimpleRouter(router, "organizations", lookup="org")
org_router.register("properties", PropertyViewSet, basename="org-properties")
org_router.register("maintenance-requests", MaintenanceRequestViewSet, basename="org-maintenance-requests")

mr_router = NestedSimpleRouter(org_router, "maintenance-requests", lookup="mr")
mr_router.register("work-orders", WorkOrderViewSet, basename="mr-work-orders")

urlpatterns = [
    path("users/", include(("app.api.authentication.urls", "authentication"), namespace="authentication")),
]

urlpatterns += router.urls + org_router.urls + mr_router.urls