from rest_framework.routers import SimpleRouter

from avatar_local.api.views import AvatarViewSets

router = SimpleRouter()
router.register("avatar", AvatarViewSets)

urlpatterns = router.urls
