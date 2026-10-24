from django.urls import path
from rest_framework.routers import SimpleRouter

from . import platform_views as v

router = SimpleRouter()
router.register("committee", v.CommitteeViewSet, basename="committee")
router.register("owner", v.OwnerViewSet, basename="owner")
router.register("admins", v.AdminViewSet, basename="admins")
router.register("hrs", v.HRViewSet, basename="hrs")
router.register("associates", v.AssociateViewSet, basename="associates")

urlpatterns = router.urls + [
    path("approvals/", v.ApprovalListView.as_view()),
    path("approvals/<uuid:pk>/decide/", v.ApprovalDecisionView.as_view()),
]