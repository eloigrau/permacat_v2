from django.db.models.query import QuerySet
from django.conf import settings


class SharedQueries:

    """Some queries that are identical for Album and Photo."""

    def is_public(self):
        """Trivial filter - will probably become more complex as time goes by!"""
        return self.filter(asso__nom="public")

    def on_site(self):
        """Return objects linked to the current site only."""
        return self.filter(sites__id=settings.SITE_ID)


class AlbumQuerySet(SharedQueries, QuerySet):
    def is_public(self):
        """Trivial filter - will probably become more complex as time goes by!"""
        return self.filter(asso__nom="public")



class PhotoQuerySet(SharedQueries, QuerySet):
    def is_public(self):
        """Trivial filter - will probably become more complex as time goes by!"""
        return self.filter()
