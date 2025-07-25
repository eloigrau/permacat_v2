import logging
import unicodedata
from importlib import import_module
from inspect import isclass
from functools import partial

import exifread
import os
import random
from PIL import Image, ImageFile, ImageFilter, ImageEnhance
from datetime import datetime
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.encoding import force_str, smart_str, filepath_to_uri
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from io import BytesIO
from sortedm2m.fields import SortedManyToManyField

from .managers import AlbumQuerySet, PhotoQuerySet
from .utils.reflection import add_reflection
from .utils.watermark import apply_watermark

from bourseLibre.models import Asso, Profil
from taggit.managers import TaggableManager
from django.utils import timezone
from bourseLibre.models import Suivis
from actstream.models import followers
from bourseLibre.settings import LOCALL
from actstream import action
from hitcount.models import HitCount
from django.utils.safestring import mark_safe
#from urlshortner.utils import shorten_url

logger = logging.getLogger('photologue.models')

# Default limit for album.latest
LATEST_LIMIT = getattr(settings, 'PHOTOLOGUE_GALLERY_LATEST_LIMIT', None)

# Number of random images from the album to display.
SAMPLE_SIZE = getattr(settings, 'PHOTOLOGUE_GALLERY_SAMPLE_SIZE', 5)

# max_length setting for the ImageModel ImageField
IMAGE_FIELD_MAX_LENGTH = getattr(settings, 'PHOTOLOGUE_IMAGE_FIELD_MAX_LENGTH', 100)

# Path to sample image
SAMPLE_IMAGE_PATH = getattr(settings, 'PHOTOLOGUE_SAMPLE_IMAGE_PATH', os.path.join(
    os.path.dirname(__file__), 'res', 'sample.jpg'))

# Modify image file buffer size.
ImageFile.MAXBLOCK = getattr(settings, 'PHOTOLOGUE_MAXBLOCK', 256 * 2 ** 10)

# Photologue image path relative to media root
PHOTOLOGUE_DIR = getattr(settings, 'PHOTOLOGUE_DIR', 'photologue')

# Look for user function to define file paths
PHOTOLOGUE_PATH = getattr(settings, 'PHOTOLOGUE_PATH', None)
if PHOTOLOGUE_PATH is not None:
    if callable(PHOTOLOGUE_PATH):
        get_storage_path = PHOTOLOGUE_PATH
    else:
        parts = PHOTOLOGUE_PATH.split('.')
        module_name = '.'.join(parts[:-1])
        module = import_module(module_name)
        get_storage_path = getattr(module, parts[-1])
else:
    def get_storage_path(instance, filename):
        fn = unicodedata.normalize('NFKD', force_str(filename)).encode('ascii', 'ignore').decode('ascii')
        return os.path.join(PHOTOLOGUE_DIR, 'photos', fn)

# Support CACHEDIR.TAG spec for backups for ignoring cache dir.
# See http://www.brynosaurus.com/cachedir/spec.html
PHOTOLOGUE_CACHEDIRTAG = os.path.join(PHOTOLOGUE_DIR, "photos", "cache", "CACHEDIR.TAG")
if not default_storage.exists(PHOTOLOGUE_CACHEDIRTAG):
    default_storage.save(PHOTOLOGUE_CACHEDIRTAG, ContentFile(
        b"Signature: 8a477f597d28d172789f06886806bc55"))

# Exif Orientation values
# Value 0thRow	0thColumn
#   1	top     left
#   2	top     right
#   3	bottom	right
#   4	bottom	left
#   5	left	top
#   6	right   top
#   7	right   bottom
#   8	left    bottom

# Image Orientations (according to EXIF informations) that needs to be
# transposed and appropriate action
IMAGE_EXIF_ORIENTATION_MAP = {
    2: Image.FLIP_LEFT_RIGHT,
    3: Image.ROTATE_180,
    6: Image.ROTATE_270,
    8: Image.ROTATE_90,
}

# Quality options for JPEG images
JPEG_QUALITY_CHOICES = (
    (30, _('Very Low')),
    (40, _('Low')),
    (50, _('Medium-Low')),
    (60, _('Medium')),
    (70, _('Medium-High')),
    (80, _('High')),
    (90, _('Very High')),
)

# choices for new crop_anchor field in Photo
CROP_ANCHOR_CHOICES = (
    ('top', _('Top')),
    ('right', _('Right')),
    ('bottom', _('Bottom')),
    ('left', _('Left')),
    ('center', _('Center (Default)')),
)

IMAGE_TRANSPOSE_CHOICES = (
    ('FLIP_LEFT_RIGHT', _('Flip left to right')),
    ('FLIP_TOP_BOTTOM', _('Flip top to bottom')),
    ('ROTATE_90', _('Rotate 90 degrees counter-clockwise')),
    ('ROTATE_270', _('Rotate 90 degrees clockwise')),
    ('ROTATE_180', _('Rotate 180 degrees')),
)

WATERMARK_STYLE_CHOICES = (
    ('tile', _('Tile')),
    ('scale', _('Scale')),
)

# Prepare a list of image filters
filter_names = []
for n in dir(ImageFilter):
    klass = getattr(ImageFilter, n)
    if isclass(klass) and issubclass(klass, ImageFilter.BuiltinFilter) and \
            hasattr(klass, 'name'):
        filter_names.append(klass.__name__)
IMAGE_FILTERS_HELP_TEXT = _('Chain multiple filters using the following pattern "FILTER_ONE->FILTER_TWO->FILTER_THREE"'
                            '. Image filters will be applied in order. The following filters are available: %s.'
                            % (', '.join(filter_names)))

size_method_map = {}


class TagField(models.CharField):
    """Tags have been removed from Photologue, but the migrations still refer to them so this
    Tagfield definition is left here.
    """

    def __init__(self, **kwargs):
        default_kwargs = {'max_length': 255, 'blank': True}
        default_kwargs.update(kwargs)
        super().__init__(**default_kwargs)

    def get_internal_type(self):
        return 'CharField'


class Album(models.Model):
    date_creation = models.DateTimeField(_('date published'),
                                      default=now)
    title = models.CharField(_('title'),
                             max_length=250,
                             unique=True)
    slug = models.SlugField(_('title slug'),
                            unique=True,
                            max_length=250,
                            help_text=_('A "slug" is a unique URL-friendly title for an object.'))
    description = models.TextField(_('Description'),
                                   blank=True)

    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
    estModifiable = models.BooleanField(default=False, verbose_name=_("Modifiable par les autres"))
    tags = TaggableManager(verbose_name=_("Mots clés"), help_text="Liste de mots-clés séparés par une virgule", blank=True)

    photos = SortedManyToManyField('photologue.Photo',
                                   related_name='albums',
                                   verbose_name=_('photos'),
                                   blank=True)
    sites = models.ManyToManyField(Site, verbose_name=_('sites'),
                                   blank=True)

    objects = AlbumQuerySet.as_manager()

    class Meta:
        ordering = ['-date_creation']
        get_latest_by = 'date_creation'
        verbose_name = _('album')
        verbose_name_plural = _('albums')

    def save(self, sendMail=True, *args, **kwargs):
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            if sendMail:
                suivi, created = Suivis.objects.get_or_create(nom_suivi='albums')
                titre = "Nouvel album"
                message = "Un album photo a été ajouté : ["+ self.asso.nom +"] '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.title + "</a>'"
                emails = [suiv.email for suiv in followers(suivi) if self.auteur != suiv and self.est_autorise(suiv)]
                if emails and not LOCALL:
                    creation = True
        else:
            if sendMail:
                titre = "Album créé"
                message = "L'album ["+ self.asso.nom +"] '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.title + "</a>' a été modifié"
                emails = [suiv.email for suiv in followers(self) if self.auteur != suiv and self.est_autorise(suiv)]

        retour = super().save(*args, **kwargs)

        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)

        return retour

    def __str__(self):
        return self.title

    @property
    def titre(self):
        return self.title

    def get_absolute_url(self):
        return reverse('photologue:album', args=[self.slug]) + "#ref-titre"

    def get_absolute_url_photos(self):
        photos = self.photos.all()
        if photos :
            return photos[0].get_absolute_url()
        else:
            return self.get_absolute_url()

    def get_photos(self):
        return self.photos.all()

    def est_autorise(self, user):
        if not self.asso:
            return True

        return self.asso.est_autorise(user)

    def latest(self, limit=LATEST_LIMIT, public=True):
        if not limit:
            limit = self.photo_count()
        if public:
            return self.photos[:limit]
        else:
            return self.photos.filter(sites__id=settings.SITE_ID)[:limit]

    def sample(self, count=None):
        """Return a sample of photos, ordered at random.
        If the 'count' is not specified, it will return a number of photos
        limited by the GALLERY_SAMPLE_SIZE setting.
        """
        if not count:
            count = SAMPLE_SIZE
        if count > self.photo_count():
            count = self.photo_count()
        photo_set = self.photos.filter(sites__id=settings.SITE_ID)
        return random.sample(set(photo_set), count)

    def photo_count(self):
        return self.photos.count()

    photo_count.short_description = _('count')

    @property
    def is_public(self):
        return self.asso.slug == "public"

    def public(self):
         """Return a queryset of all the public photos in this album."""
         return self.photos.all()

    def get_photo_sample(self):
        return self.photos.all()[:1]

class Document(models.Model):
    doc = models.FileField('Document',
                            max_length=IMAGE_FIELD_MAX_LENGTH,
                            upload_to='documents/%Y/%m/%d', )

    titre = models.CharField(_('titre'),
                             max_length=250,
                             unique=True)
    slug = models.SlugField(_('slug'),
                            unique=True,
                            max_length=250,
                            help_text=_('A "slug" is a unique URL-friendly title for an object.'))
    date_creation = models.DateTimeField(_("date d'ajout"), auto_now_add =True)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    tags = TaggableManager(verbose_name=_("Mots clés"), help_text="Liste de mots-clés séparés par une virgule", blank=True)

    article = models.ForeignKey('blog.Article', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.titre + " (" + str(self.doc) +")"

    def get_delete_url(self):
        return reverse("photologue:supprimerDocument", kwargs={"slug":self.slug})

    def get_change_url(self):
        return reverse("photologue:modifierDocument", kwargs={"slug":self.slug})

    def save(self, sendMail=True, *args, **kwargs):
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            if sendMail:
                suivi, created = Suivis.objects.get_or_create(nom_suivi='albums')
                emails = [suiv.email for suiv in followers(suivi) if self.auteur != suiv and self.est_autorise(suiv)]


        retour = super().save(*args, **kwargs)

        if emails:
            titre = "Nouveau document"
            message = "Un document a été ajouté : [" + self.asso.nom + "] '<a href='https://www.perma.cat" + self.doc.url + "'>" + self.titre + "</a>'"
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)

        return retour

    def get_absolute_url(self):
        if self.article:
            return self.article.get_absolute_url()
        #return reverse('photologue:doc-list')
        return self.doc.url


    def est_autorise(self, user):
        if not self.asso:
            return True
        return self.asso.est_autorise(user)

    @property
    def getHitNumber(self,):
        return HitCount.objects.get_for_object(self).hits

    @property
    def get_logo_nomgroupe_html(self,):
        return self.asso.get_logo_nomgroupe_html_taille(taille=18)

class ImageModel(models.Model):
    image = models.ImageField(_('image'),
                              max_length=IMAGE_FIELD_MAX_LENGTH,
                              upload_to="photologue",
                              help_text = 'max. 20 Mo')
                              #upload_to=get_storage_path)
    date_taken = models.DateTimeField(_('date taken'),
                                      null=True,
                                      blank=True,
                                      help_text=_('Date image was taken; is obtained from the image EXIF data.'))
    view_count = models.PositiveIntegerField(_('view count'),
                                             default=0,
                                             editable=False)
    crop_from = models.CharField(_('crop from'),
                                 blank=True,
                                 max_length=10,
                                 default='center',
                                 choices=CROP_ANCHOR_CHOICES)
    effect = models.ForeignKey('photologue.PhotoEffect',
                               null=True,
                               blank=True,
                               related_name="%(class)s_related",
                               verbose_name=_('effect'),
                               on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def EXIF(self, file=None):
        try:
            if file:
                tags = exifread.process_file(file)
            else:
                with self.image.storage.open(self.image.name, 'rb') as file:
                    tags = exifread.process_file(file, details=False)
            return tags
        except:
            return {}

    # def admin_thumbnail(self):
    #     func = getattr(self, 'get_admin_thumbnail_url', None)
    #     if func is None:
    #         return _('An "admin_thumbnail" photo size has not been defined.')
    #     else:
    #         if hasattr(self, 'get_absolute_url'):
    #             return mark_safe('<a href="{}"><img src="{}"></a>'.format(self.get_absolute_url(), func()))
    #         else:
    #             return mark_safe('<a href="{}"><img src="{}"></a>'.format(self.image.url, func()))
    #
    # admin_thumbnail.short_description = _('Thumbnail')
    # admin_thumbnail.allow_tags = True

    def cache_path(self):
        return os.path.join(os.path.dirname(self.image.name), "cache")

    def cache_url(self):
        return '/'.join([os.path.dirname(self.image.url), "cache"])

    def image_filename(self):
        return os.path.basename(force_str(self.image.name))

    def _get_filename_for_size(self, size):
        size = getattr(size, 'name', size)
        base, ext = os.path.splitext(self.image_filename())
        return ''.join([base, '_', size, ext])

    def _get_SIZE_photosize(self, size):
        return PhotoSizeCache().sizes.get(size)

    def _get_SIZE_size(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        try:
            return Image.open(self.image.storage.open(
                self._get_SIZE_filename(size))).size
        except:
            return None

    def _get_SIZE_url(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        if not self.size_exists(photosize):
            self.create_size(photosize)
        if photosize.increment_count:
            self.increment_count()
        return '/'.join([
            self.cache_url(),
            filepath_to_uri(self._get_filename_for_size(photosize.name))])

    def _get_SIZE_filename(self, size):
        photosize = PhotoSizeCache().sizes.get(size)
        return smart_str(os.path.join(self.cache_path(),
                                      self._get_filename_for_size(photosize.name)))

    def increment_count(self):
        self.view_count += 1
        models.Model.save(self)

    def __getattr__(self, name):
        global size_method_map
        if not size_method_map:
            init_size_method_map()
        di = size_method_map.get(name, None)
        if di is not None:
            result = partial(getattr(self, di['base_name']), di['size'])
            setattr(self, name, result)
            return result
        else:
            raise AttributeError

    def size_exists(self, photosize):
        func = getattr(self, "get_%s_filename" % photosize.name, None)
        if func is not None:
            if self.image.storage.exists(func()):
                return True
        return False

    def resize_image(self, im, photosize):
        cur_width, cur_height = im.size
        new_width, new_height = photosize.size
        if photosize.crop:
            ratio = max(float(new_width) / cur_width, float(new_height) / cur_height)
            x = (cur_width * ratio)
            y = (cur_height * ratio)
            xd = abs(new_width - x)
            yd = abs(new_height - y)
            x_diff = int(xd / 2)
            y_diff = int(yd / 2)
            if self.crop_from == 'top':
                box = (int(x_diff), 0, int(x_diff + new_width), new_height)
            elif self.crop_from == 'left':
                box = (0, int(y_diff), new_width, int(y_diff + new_height))
            elif self.crop_from == 'bottom':
                # y - yd = new_height
                box = (int(x_diff), int(yd), int(x_diff + new_width), int(y))
            elif self.crop_from == 'right':
                # x - xd = new_width
                box = (int(xd), int(y_diff), int(x), int(y_diff + new_height))
            else:
                box = (int(x_diff), int(y_diff), int(x_diff + new_width), int(y_diff + new_height))
            im = im.resize((int(x), int(y)), Image.Resampling.LANCZOS).crop(box)
        else:
            if not new_width == 0 and not new_height == 0:
                ratio = min(float(new_width) / cur_width,
                            float(new_height) / cur_height)
            else:
                if new_width == 0:
                    ratio = float(new_height) / cur_height
                else:
                    ratio = float(new_width) / cur_width
            new_dimensions = (int(round(cur_width * ratio)),
                              int(round(cur_height * ratio)))
            if new_dimensions[0] > cur_width or \
                    new_dimensions[1] > cur_height:
                if not photosize.upscale:
                    return im
            im = im.resize(new_dimensions, Image.Resampling.LANCZOS)
        return im

    def create_size(self, photosize, recreate=False):
        if self.size_exists(photosize) and not recreate:
            return
        try:
            im = Image.open(self.image.storage.open(self.image.name))
        except OSError:
            return
        # Save the original format
        im_format = im.format
        # Apply effect if found
        if self.effect is not None:
            im = self.effect.pre_process(im)
        elif photosize.effect is not None:
            im = photosize.effect.pre_process(im)
        # Rotate if found & necessary
        if 'Image Orientation' in self.EXIF() and \
                self.EXIF().get('Image Orientation').values[0] in IMAGE_EXIF_ORIENTATION_MAP:
            im = im.transpose(
                IMAGE_EXIF_ORIENTATION_MAP[self.EXIF().get('Image Orientation').values[0]])
        # Resize/crop image
        if (im.size != photosize.size and photosize.size != (0, 0)) or recreate:
            im = self.resize_image(im, photosize)
        # Apply watermark if found
        if photosize.watermark is not None:
            im = photosize.watermark.post_process(im)
        # Apply effect if found
        if self.effect is not None:
            im = self.effect.post_process(im)
        elif photosize.effect is not None:
            im = photosize.effect.post_process(im)
        # Save file
        im_filename = getattr(self, "get_%s_filename" % photosize.name)()
        try:
            buffer = BytesIO()
            if im_format != 'JPEG':
                im.save(buffer, im_format)
            else:
                # Issue #182 - test fix from https://github.com/bashu/django-watermark/issues/31
                if im.mode.endswith('A'):
                    im = im.convert(im.mode[:-1])
                im.save(buffer, 'JPEG', quality=int(photosize.quality),
                        optimize=True)
            buffer_contents = ContentFile(buffer.getvalue())
            self.image.storage.save(im_filename, buffer_contents)
        except OSError as e:
            if self.image.storage.exists(im_filename):
                self.image.storage.delete(im_filename)
            raise e

    def remove_size(self, photosize, remove_dirs=True):
        if not self.size_exists(photosize):
            return
        filename = getattr(self, "get_%s_filename" % photosize.name)()
        if self.image.storage.exists(filename):
            self.image.storage.delete(filename)

    def clear_cache(self):
        cache = PhotoSizeCache()
        for photosize in cache.sizes.values():
            self.remove_size(photosize, False)

    def pre_cache(self, recreate=False):
        cache = PhotoSizeCache()
        if recreate:
            self.clear_cache()
        for photosize in cache.sizes.values():
            if photosize.pre_cache:
                self.create_size(photosize, recreate)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_image = self.image

    def save(self, *args, **kwargs):
        recreate = kwargs.pop('recreate', False)
        image_has_changed = False
        if self._get_pk_val() and (self._old_image != self.image):
            image_has_changed = True
            # If we have changed the image, we need to clear from the cache all instances of the old
            # image; clear_cache() works on the current (new) image, and in turn calls several other methods.
            # Changing them all to act on the old image was a lot of changes, so instead we temporarily swap old
            # and new images.
            new_image = self.image
            self.image = self._old_image
            self.clear_cache()
            self.image = new_image  # Back to the new image.
            self._old_image.storage.delete(self._old_image.name)  # Delete (old) base image.
        if self.date_taken is None or image_has_changed:
            # Attempt to get the date the photo was taken from the EXIF data.
            try:
                exif_date = self.EXIF(self.image.file).get('EXIF DateTimeOriginal', None)
                if exif_date is not None:
                    d, t = exif_date.values.split()
                    year, month, day = d.split(':')
                    hour, minute, second = t.split(':')
                    self.date_taken = datetime(int(year), int(month), int(day),
                                               int(hour), int(minute), int(second))
            except:
                logger.error('Failed to read EXIF DateTimeOriginal', exc_info=True)
        super().save(*args, **kwargs)
        self.pre_cache(recreate)

    def delete(self):
        assert self._get_pk_val() is not None, \
            "%s object can't be deleted because its %s attribute is set to None." % \
            (self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        # Files associated to a FileField have to be manually deleted:
        # https://docs.djangoproject.com/en/dev/releases/1.3/#deleting-a-model-doesn-t-delete-associated-files
        # http://haineault.com/blog/147/
        # The data loss scenarios mentioned in the docs hopefully do not apply
        # to Photologue!
        super().delete()
        self.image.storage.delete(self.image.name)


class Photo(ImageModel):
    title = models.CharField(_('title'),
                             max_length=250,
                             unique=False, blank=True)
    slug = models.SlugField(_('slug'),
                            unique=True,
                            max_length=250,
                            help_text=_('A "slug" is a unique URL-friendly title for an object.'))
    caption = models.TextField(_('caption'), blank=True)
    date_creation = models.DateTimeField(_('date added'), default=now)
    sites = models.ManyToManyField(Site, verbose_name=_('sites'),blank=True)


    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
    tags = TaggableManager(verbose_name=_("Mots clés"), help_text="Liste de mots-clés séparés par une virgule", blank=True)
    objects = PhotoQuerySet.as_manager()

    class Meta:
        ordering = ['-date_creation']
        get_latest_by = 'date_creation'
        verbose_name = _("photo")
        verbose_name_plural = _("photos")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If crop_from or effect property has been changed on existing image,
        # update kwargs to force image recreation in parent class
        current = Photo.objects.get(pk=self.pk) if self.pk else None
        if current and (current.crop_from != self.crop_from or current.effect != self.effect):
            kwargs.update(recreate=True)

        if self.slug is None:
            self.slug = slugify(self.title)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('photologue:photo', kwargs={'slug':self.slug}) + "#photos"

    def get_album(self):
        albums = self.albums.filter()
        if albums:
            return albums[0]
        return None

    def get_album_url(self):
        album = self.get_album()
        if album:
            return album.get_absolute_url()
        else:
            return reverse('photologue:album-list')

    def get_asso(self):
        return

    def public_galleries(self):
        """Return the public galleries to which this photo belongs."""
        return self.albums.filter()

    def get_previous_in_album(self, album=None):
        """Find the neighbour of this photo in the supplied album.
        We assume that the album and all its photos are on the same site.
        """
        if not album:
            album = self.get_album()
        if not album:
            raise ValueError('Photo does not belong to album.')

        photos = album.get_photos()
        if self not in photos:
            raise ValueError('Photo does not belong to album.')
        previous = None
        for photo in photos:
            if photo == self:
                return previous
            previous = photo

    def get_next_in_album(self, album=None):
        """Find the neighbour of this photo in the supplied album.
        We assume that the album and all its photos are on the same site.
        """
        if not album:
            album = self.get_album()
        if not album:
            raise ValueError('Photo does not belong to album.')
        photos = album.get_photos()
        if self not in photos:
            raise ValueError('Photo does not belong to album.')
        matched = False
        for photo in photos:
            if matched:
                return photo
            if photo == self:
                matched = True
        return None


class BaseEffect(models.Model):
    name = models.CharField(_('name'),
                            max_length=30,
                            unique=True)
    description = models.TextField(_('description'),
                                   blank=True)

    class Meta:
        abstract = True

    def sample_dir(self):
        return os.path.join(PHOTOLOGUE_DIR, 'samples')

    def sample_url(self):
        return settings.MEDIA_URL + '/'.join([PHOTOLOGUE_DIR, 'samples',
                                              '{} {}.jpg'.format(self.name.lower(), 'sample')])

    def sample_filename(self):
        return os.path.join(self.sample_dir(), '{} {}.jpg'.format(self.name.lower(), 'sample'))

    def create_sample(self):
        try:
            im = Image.open(SAMPLE_IMAGE_PATH)
        except OSError:
            raise OSError(
                'Photologue was unable to open the sample image: %s.' % SAMPLE_IMAGE_PATH)
        im = self.process(im)
        buffer = BytesIO()
        # Issue #182 - test fix from https://github.com/bashu/django-watermark/issues/31
        if im.mode.endswith('A'):
            im = im.convert(im.mode[:-1])
        im.save(buffer, 'JPEG', quality=90, optimize=True)
        buffer_contents = ContentFile(buffer.getvalue())
        default_storage.save(self.sample_filename(), buffer_contents)

    def admin_sample(self):
        return '<img src="%s">' % self.sample_url()

    admin_sample.short_description = 'Sample'
    admin_sample.allow_tags = True

    def pre_process(self, im):
        return im

    def post_process(self, im):
        return im

    def process(self, im):
        im = self.pre_process(im)
        im = self.post_process(im)
        return im

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            default_storage.delete(self.sample_filename())
        except:
            pass
        models.Model.save(self, *args, **kwargs)
        self.create_sample()
        for size in self.photo_sizes.all():
            size.clear_cache()
        # try to clear all related subclasses of ImageModel
        for prop in [prop for prop in dir(self) if prop[-8:] == '_related']:
            for obj in getattr(self, prop).all():
                obj.clear_cache()
                obj.pre_cache()

    def delete(self):
        try:
            default_storage.delete(self.sample_filename())
        except:
            pass
        models.Model.delete(self)


class PhotoEffect(BaseEffect):
    """ A pre-defined effect to apply to photos """
    transpose_method = models.CharField(_('rotate or flip'),
                                        max_length=15,
                                        blank=True,
                                        choices=IMAGE_TRANSPOSE_CHOICES)
    color = models.FloatField(_('color'),
                              default=1.0,
                              help_text=_('A factor of 0.0 gives a black and white image, a factor of 1.0 gives the '
                                          'original image.'))
    brightness = models.FloatField(_('brightness'),
                                   default=1.0,
                                   help_text=_('A factor of 0.0 gives a black image, a factor of 1.0 gives the '
                                               'original image.'))
    contrast = models.FloatField(_('contrast'),
                                 default=1.0,
                                 help_text=_('A factor of 0.0 gives a solid grey image, a factor of 1.0 gives the '
                                             'original image.'))
    sharpness = models.FloatField(_('sharpness'),
                                  default=1.0,
                                  help_text=_('A factor of 0.0 gives a blurred image, a factor of 1.0 gives the '
                                              'original image.'))
    filters = models.CharField(_('filters'),
                               max_length=200,
                               blank=True,
                               help_text=_(IMAGE_FILTERS_HELP_TEXT))
    reflection_size = models.FloatField(_('size'),
                                        default=0,
                                        help_text=_('The height of the reflection as a percentage of the orignal '
                                                    'image. A factor of 0.0 adds no reflection, a factor of 1.0 adds a'
                                                    ' reflection equal to the height of the orignal image.'))
    reflection_strength = models.FloatField(_('strength'),
                                            default=0.6,
                                            help_text=_('The initial opacity of the reflection gradient.'))
    background_color = models.CharField(_('color'),
                                        max_length=7,
                                        default="#FFFFFF",
                                        help_text=_('The background color of the reflection gradient. Set this to '
                                                    'match the background color of your page.'))

    class Meta:
        verbose_name = _("photo effect")
        verbose_name_plural = _("photo effects")

    def pre_process(self, im):
        if self.transpose_method != '':
            method = getattr(Image, self.transpose_method)
            im = im.transpose(method)
        if im.mode != 'RGB' and im.mode != 'RGBA':
            return im
        for name in ['Color', 'Brightness', 'Contrast', 'Sharpness']:
            factor = getattr(self, name.lower())
            if factor != 1.0:
                im = getattr(ImageEnhance, name)(im).enhance(factor)
        for name in self.filters.split('->'):
            image_filter = getattr(ImageFilter, name.upper(), None)
            if image_filter is not None:
                try:
                    im = im.filter(image_filter)
                except ValueError:
                    pass
        return im

    def post_process(self, im):
        if self.reflection_size != 0.0:
            im = add_reflection(im, bgcolor=self.background_color,
                                amount=self.reflection_size, opacity=self.reflection_strength)
        return im


class Watermark(BaseEffect):
    image = models.ImageField(_('image'),
                              upload_to=PHOTOLOGUE_DIR + "/watermarks")
    style = models.CharField(_('style'),
                             max_length=5,
                             choices=WATERMARK_STYLE_CHOICES,
                             default='scale')
    opacity = models.FloatField(_('opacity'),
                                default=1,
                                help_text=_("The opacity of the overlay."))

    class Meta:
        verbose_name = _('watermark')
        verbose_name_plural = _('watermarks')

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." \
                                               % (self._meta.object_name, self._meta.pk.attname)
        super().delete()
        self.image.storage.delete(self.image.name)

    def post_process(self, im):
        mark = Image.open(self.image.storage.open(self.image.name))
        return apply_watermark(im, mark, self.style, self.opacity)


class PhotoSize(models.Model):
    """About the Photosize name: it's used to create get_PHOTOSIZE_url() methods,
    so the name has to follow the same restrictions as any Python method name,
    e.g. no spaces or non-ascii characters."""

    name = models.CharField(_('name'),
                            max_length=40,
                            unique=True,
                            help_text=_(
                                'Photo size name should contain only letters, numbers and underscores. Examples: '
                                '"thumbnail", "display", "small", "main_page_widget".'),
                            validators=[RegexValidator(regex='^[a-z0-9_]+$',
                                                       message='Use only plain lowercase letters (ASCII), numbers and '
                                                               'underscores.'
                                                       )]
                            )
    width = models.PositiveIntegerField(_('width'),
                                        default=0,
                                        help_text=_(
                                            'If width is set to "0" the image will be scaled to the supplied height.'))
    height = models.PositiveIntegerField(_('height'),
                                         default=0,
                                         help_text=_(
                                             'If height is set to "0" the image will be scaled to the supplied width'))
    quality = models.PositiveIntegerField(_('quality'),
                                          choices=JPEG_QUALITY_CHOICES,
                                          default=70,
                                          help_text=_('JPEG image quality.'))
    upscale = models.BooleanField(_('upscale images?'),
                                  default=False,
                                  help_text=_('If selected the image will be scaled up if necessary to fit the '
                                              'supplied dimensions. Cropped sizes will be upscaled regardless of this '
                                              'setting.')
                                  )
    crop = models.BooleanField(_('crop to fit?'),
                               default=False,
                               help_text=_('If selected the image will be scaled and cropped to fit the supplied '
                                           'dimensions.'))
    pre_cache = models.BooleanField(_('pre-cache?'),
                                    default=False,
                                    help_text=_('If selected this photo size will be pre-cached as photos are added.'))
    increment_count = models.BooleanField(_('increment view count?'),
                                          default=False,
                                          help_text=_('If selected the image\'s "view_count" will be incremented when '
                                                      'this photo size is displayed.'))
    effect = models.ForeignKey('photologue.PhotoEffect',
                               null=True,
                               blank=True,
                               related_name='photo_sizes',
                               verbose_name=_('photo effect'),
                               on_delete=models.CASCADE)
    watermark = models.ForeignKey('photologue.Watermark',
                                  null=True,
                                  blank=True,
                                  related_name='photo_sizes',
                                  verbose_name=_('watermark image'),
                                  on_delete=models.CASCADE)

    class Meta:
        ordering = ['width', 'height']
        verbose_name = _('photo size')
        verbose_name_plural = _('photo sizes')

    def __str__(self):
        return self.name

    def clear_cache(self):
        for cls in ImageModel.__subclasses__():
            for obj in cls.objects.all():
                obj.remove_size(self)
                if self.pre_cache:
                    obj.create_size(self)
        PhotoSizeCache().reset()

    def clean(self):
        if self.crop is True:
            if self.width == 0 or self.height == 0:
                raise ValidationError(
                    _("Can only crop photos if both width and height dimensions are set."))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        PhotoSizeCache().reset()
        self.clear_cache()

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." \
                                               % (self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        super().delete()

    def _get_size(self):
        return (self.width, self.height)

    def _set_size(self, value):
        self.width, self.height = value

    size = property(_get_size, _set_size)


class PhotoSizeCache:
    __state = {"sizes": {}}

    def __init__(self):
        self.__dict__ = self.__state
        if not len(self.sizes):
            sizes = PhotoSize.objects.all()
            for size in sizes:
                self.sizes[size.name] = size

    def reset(self):
        global size_method_map
        size_method_map = {}
        self.sizes = {}


def init_size_method_map():
    global size_method_map
    for size in PhotoSizeCache().sizes.keys():
        size_method_map['get_%s_size' % size] = \
            {'base_name': '_get_SIZE_size', 'size': size}
        size_method_map['get_%s_photosize' % size] = \
            {'base_name': '_get_SIZE_photosize', 'size': size}
        size_method_map['get_%s_url' % size] = \
            {'base_name': '_get_SIZE_url', 'size': size}
        size_method_map['get_%s_filename' % size] = \
            {'base_name': '_get_SIZE_filename', 'size': size}


def add_default_site(instance, created, **kwargs):
    """
    Called via Django's signals when an instance is created.
    In case PHOTOLOGUE_MULTISITE is False, the current site (i.e.
    ``settings.SITE_ID``) will always be added to the site relations if none are
    present.
    """
    if not created:
        return
    if getattr(settings, 'PHOTOLOGUE_MULTISITE', False):
        return
    if instance.sites.exists():
        return
    instance.sites.add(Site.objects.get_current())


post_save.connect(add_default_site, sender=Album)
post_save.connect(add_default_site, sender=Photo)



class Document_recherche(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True,
                                 #help_text=mark_safe("<p style='color:teal'>Min 2 lettres</p>")
                               )