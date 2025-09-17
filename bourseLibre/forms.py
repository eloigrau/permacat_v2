from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Produit, Produit_aliment, Produit_objet, Produit_service, Produit_vegetal, Adresse, \
    Asso, Profil, Message, MessageGeneral, Message_salon, InscriptionNewsletter, Adhesion_permacat, \
    Produit_offresEtDemandes, Salon, InscritSalon, Adhesion_asso, Monnaie, Profil_recherche, EvenementSalon, Favoris, \
    Lien_AssoSalon
from local_summernote.widgets import SummernoteWidget
from blog.forms import SummernoteWidgetWithCustomToolbar
from django.utils import timezone
from django.core.exceptions import ValidationError
from blog.models import Article
from dal import autocomplete
from local_captcha.fields import CaptchaField
from adherents.models import Adherent
from django.utils.translation import gettext_lazy as _

#from .constantes import Choix
#from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea


fieldsCommunsProduits = ['souscategorie', 'nom_produit', 'description', 'estUneOffre', 'asso',
                         'monnaies', 'prix', 'date_debut', 'date_expiration', ]


class ProduitCreationForm(forms.ModelForm):
    estUneOffre = forms.ChoiceField(choices=((1, "Offre"), (0, "Demande")), label="L'annonce est une offre (vous donnez..) ou une demande (vous cherchez...) ?", required=True)
    asso = forms.ModelChoiceField(queryset=Asso.objects.all().order_by("id"), required=True, label="Annonce publique ou réservée aux membres du groupe :", )
    monnaies = forms.ModelMultipleChoiceField(label='Monnaie(s)', required=False, queryset=Monnaie.objects.all(),
                                              widget=forms.CheckboxSelectMultiple(attrs={'class': 'cbox_asso', }))

    class Meta:
        model = Produit
        exclude = ('user',)

        fields = ['nom_produit', 'description', 'date_debut', 'estUneOffre', 'asso', 'date_expiration', 'monnaies', 'prix', ]
        widgets = {
            'date_debut': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }, ),
            'date_expiration': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'description': SummernoteWidget(),
        }

    def __init__(self, request, *args, **kwargs):
        super(ProduitCreationForm, self).__init__(*args, **kwargs)
        self.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if x.est_autorise(request.user)]

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_debut")
        date_expiration = cleaned_data.get("date_expiration")
        if date_debut and date_expiration:
            # Only do something if both fields are valid so far.
            if date_debut > date_expiration:
                raise forms.ValidationError(
                    "La date de fin doit etre après la date de début"
                )
        return self.cleaned_data


class ProduitModifierForm(ProduitCreationForm):
    monnaies = forms.ModelMultipleChoiceField(label='Monnaie(s)', required=False, queryset=Monnaie.objects.all(),
                                              widget=forms.CheckboxSelectMultiple(attrs={'class': 'cbox_asso', }))

    def __init__(self, *args, **kwargs):
        super(ProduitModifierForm, self).__init__(*args, **kwargs)
        self.fields["estUneOffre"].choices = ((1, "Offre"), (0, "Demande")) if kwargs[
            'instance'].estUneOffre else ((0, "Demande"), (1, "Offre"),)


class Produit_aliment_CreationForm(ProduitCreationForm):
    class Meta:
        model = Produit_aliment
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }, ),
            'date_expiration': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'description': SummernoteWidget(),
        }


class Produit_aliment_modifier_form(Produit_aliment_CreationForm, ProduitModifierForm):
    pass


class Produit_vegetal_CreationForm(ProduitCreationForm):
    class Meta:
        model = Produit_vegetal
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }, ),
            'date_expiration': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'description': SummernoteWidget(),
        }


class Produit_vegetal_modifier_form(Produit_vegetal_CreationForm, ProduitModifierForm):
    pass
    #
    # def __init__(self, *args, **kwargs):
    #     super(Produit_vegetal_modifier_form, self).__init__(*args, **kwargs)
    #     self.fields["estPublique"].choices = ((1, "Annonce publique"), (0, "Annonce réservée aux adhérents")) if kwargs[
    #         'instance'].estPublique else ((0, "Annonce réservée aux adhérents"),(1, "Annonce publique"),)
    #     self.fields["estUneOffre"].choices = ((1, "Offre"), (0, "Demande")) if kwargs[
    #         'instance'].estUneOffre else ((0, "Demande"), (1, "Offre"), )


class Produit_service_CreationForm(ProduitCreationForm):
    class Meta:
        model = Produit_service
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }, ),
            'date_expiration': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'description': SummernoteWidget(),
        }


class Produit_service_modifier_form(Produit_service_CreationForm, ProduitModifierForm):
    pass
    # def __init__(self, *args, **kwargs):
    #     super(Produit_service_modifier_form, self).__init__(*args, **kwargs)
    #     self.fields["estPublique"].choices = ((1, "Annonce publique"), (0, "Annonce réservée aux adhérents")) if \
    #     kwargs[
    #         'instance'].estPublique else ((0, "Annonce réservée aux adhérents"), (1, "Annonce publique"),)
    #     self.fields["estUneOffre"].choices = ((1, "Offre"), (0, "Demande")) if kwargs[
    #         'instance'].estUneOffre else ((0, "Demande"), (1, "Offre"),)


class Produit_objet_CreationForm(ProduitCreationForm):
    class Meta:
        model = Produit_objet
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'date_expiration': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'description': SummernoteWidget(),
        }


class Produit_offresEtDemandes_CreationForm(ProduitCreationForm):
    class Meta:
        model = Produit_offresEtDemandes
        fields = ['nom_produit', 'description', 'asso', 'date_debut', 'date_expiration', ]
        widgets = {
            'date_debut': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'date_expiration': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'description': SummernoteWidget(),
        }


class Produit_objet_modifier_form(Produit_objet_CreationForm, ProduitModifierForm):
    pass


class Produit_offresEtDemandes_modifier_form(ProduitModifierForm):
    class Meta:
        model = Produit_offresEtDemandes
        fields = ['nom_produit', 'description', 'asso',
                  'monnaies', 'prix', 'date_debut', 'date_expiration', ]
        widgets = {
            'date_debut': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'date_expiration': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'description': SummernoteWidget(),
        }

    pass


class AdresseForm(forms.ModelForm):
    rue = forms.CharField(
        label="Rue (à peu près, champs invisible par les autres membres mais pour un affichage sur la carte)",
        required=False)
    code_postal = forms.CharField(label="Code postal*", initial="66000", required=False)
    commune = forms.CharField(label="Commune", initial="Perpignan", required=False)
    telephone = forms.CharField(label="Téléphone", required=False)
    pays = forms.CharField(label="Pays", initial="France", required=False)
    latitude = forms.FloatField(label="Latitude", initial="42", required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(label="Longitude", initial="2", required=False, widget=forms.HiddenInput())

    class Meta:
        model = Adresse
        exclude = ('latitude', 'longitude')

    def save(self, *args, **kwargs):
        adresse = super(AdresseForm, self).save(commit=False)
        adresse.save()
        return adresse


class AdresseForm2(forms.ModelForm):
    telephone = forms.CharField(label="Contact (tel/mail/...)", required=False)
    latitude = forms.FloatField(label="Latitude", required=True)
    longitude = forms.FloatField(label="Longitude", required=True)

    class Meta:
        model = Adresse
        fields = ('latitude', 'longitude', 'commune', 'code_postal', 'telephone')

    def save(self, *args, **kwargs):
        #self.cleaned_data['latitude'] = float(self.cleaned_data['latitude'])
        adresse = super(AdresseForm2, self).save(commit=False)
        adresse.save()
        return adresse


class AdresseForm3(forms.ModelForm):
    latitude = forms.FloatField(label="Latitude", initial="42,2", required=True)
    longitude = forms.FloatField(label="Longitude", initial="2,2", required=True)

    class Meta:
        model = Adresse
        exclude = ('rue', 'commune', 'code_postal', 'pays', 'telephone')

    def save(self, *args, **kwargs):
        #self.cleaned_data['latitude'] = float(self.cleaned_data['latitude'])
        adresse = super(AdresseForm3, self).save(commit=False)
        adresse.save()
        return adresse


class AdresseForm4(forms.ModelForm):
    latitude = forms.FloatField(label="Latitude", initial="", required=False)
    longitude = forms.FloatField(label="Longitude", initial="", required=False)

    class Meta:
        model = Adresse
        fields = ['commune', 'code_postal', 'latitude', 'longitude']

    def save(self, *args, **kwargs):
        adresse = super(AdresseForm4, self).save(commit=False)
        if not adresse.latitude or not adresse.longitude:
            adresse.set_latlon_from_adresse()

        adresse.save()
        return adresse


class AdresseForm5(forms.ModelForm):
    rue = forms.CharField(
        label="Rue",
        required=False)
    latitude = forms.FloatField(label="Latitude", initial="", required=False)
    longitude = forms.FloatField(label="Longitude", initial="", required=False)
    telephone = forms.CharField(label="Téléphone", required=False)

    class Meta:
        model = Adresse
        fields = ['rue', 'commune', 'code_postal', 'latitude', 'longitude', 'telephone']

    def save(self, *args, **kwargs):
        adresse = super(AdresseForm5, self).save(commit=False)
        #if not adresse.latitude or not adresse.longitude:
        #   adresse.set_latlon_from_adresse()

        adresse.save()
        return adresse

    def __init__(self, request, *args, **kargs):
        super(AdresseForm5, self).__init__(request, *args, **kargs)
        field = self.fields['latitude']
        field.widget = field.hidden_widget()
        field2 = self.fields['longitude']
        field2.widget = field2.hidden_widget()


class ProfilCreationForm(UserCreationForm):
    username = forms.CharField(label="Pseudonyme (sans espace)",
                               help_text="Attention : Pas d'espace, et les majuscules sont importantes...")
    description = forms.CharField(label="Présentez-vous brièvement", help_text="Une description de vous même", required=False,
                                  widget=forms.Textarea)
    competences = forms.CharField(label="Vos compétences",
                                  help_text="Par exemple: electricien, bouturage, aromatherapie, pépinieriste, etc...",
                                  required=False, widget=forms.Textarea, )
    site_web = forms.CharField(label="Votre site web", help_text="n'oubliez pas le https://", required=False)
    #captcha = CaptchaField()
    email = forms.EmailField(label="Email*", )

    #statut_adhesion = forms.ChoiceField(choices=Choix.statut_adhesion, label='', required=True)
    adherent_pc = forms.BooleanField(required=False, label="Je suis adhérent-e de l'asso 'Permacat'")
    adherent_rtg = forms.BooleanField(required=False, label="Je suis adhérent-e de l'asso 'Ramène Ta Graine'")
    adherent_scic = forms.BooleanField(required=False, label="Je suis adhérent-e de l'asso 'PermAgora'")
    adherent_jp = forms.BooleanField(required=False, label="Je suis intéressé-e par les jardins partagés")
    adherent_ssa = forms.BooleanField(required=False, label="Je suis intéressé-e par le collectif pour expérimenter une forme de SSA dans le 66")
    #adherent_gt = forms.BooleanField(required=False, label="Je suis adhérent de l'asso 'Gardiens de la Terre'")
    #adherent_ame = forms.BooleanField(required=False, label="Je suis adhérent de l'asso 'Animal Mieux Etre'")
    accepter_annuaire = forms.BooleanField(required=False, initial=True,
                                           label="J'accepte d'apparaitre dans l'annuaire du site et la carte et rend mon profil visible par tous les inscrits")
    inscrit_newsletter = forms.BooleanField(required=False, initial=True,
                                            label="J'accepte de m'abonner aux emails de Perma.cat")
    accepter_conditions = forms.BooleanField(required=True,
                                             label="J'ai lu et j'accepte les Conditions Générales d'Utilisation du site", )

    #pseudo_june = forms.CharField(label="Pseudonyme dans le réseau de la monnaie libre",  help_text="Si vous avez un compte en June",required=False)

    def __init__(self, request, *args, **kargs):
        super(ProfilCreationForm, self).__init__(request, *args, **kargs)
        self.fields['description'].strip = False
        self.fields['competences'].strip = False

    class Meta(UserCreationForm):
        model = Profil
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'site_web', 'description',
                  'competences', 'adherent_jp', 'adherent_pc', 'adherent_rtg', 'adherent_scic', 'adherent_viure',
                  'adherent_bzz2022', 'adherent_ssa', 'inscrit_newsletter', 'accepter_annuaire', 'accepter_conditions']
        exclude = ['slug', ]

    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if Profil.objects.filter(email=email).exists():
            raise ValidationError("Désolé, un compte avec cet email existe déjà")
        if Profil.objects.filter(username__iexact=username).exists():
            raise ValidationError("Désolé, un compte avec cet identifiant existe déjà")
        return self.cleaned_data

    def save(self, commit=True, is_active=False):
        return super(ProfilCreationForm, self).save(commit)
        self.is_active = is_active
        return instance


class ProfilChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's password hash display field.
    """
    email = forms.EmailField(label="Email")
    username = forms.CharField(label="Pseudonyme",
                               help_text="Attention : Pas d'espace, et les majuscules sont importantes...")
    description = forms.CharField(label="Description", help_text="Une description de vous même",
                                  widget=SummernoteWidget, required=False)
    competences = forms.CharField(label="Savoir-faire",
                                  help_text="Par exemple: electricien, bouturage, aromatherapie, etc...",
                                  widget=SummernoteWidget, required=False)
    inscrit_newsletter = forms.BooleanField(required=False)
    accepter_annuaire = forms.BooleanField(required=False,
                                           label="J'accepte d'apparaitre dans l'annuaire du site et la carte et rend mon profil visible par tous")
    password = None

    def __init__(self, *args, **kargs):
        super(ProfilChangeForm, self).__init__(*args, **kargs)
        self.fields['description'].strip = False
        self.fields['competences'].strip = False

    class Meta:
        model = Profil
        fields = ['username', 'first_name', 'last_name', 'email', 'site_web', 'description', 'competences',
                  'pseudo_june', 'accepter_annuaire', 'inscrit_newsletter', 'css_dark', 'language']


class ProfilChangeForm_admin(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    email = forms.EmailField(label="Email")
    username = forms.CharField(label="Pseudonyme")
    description = forms.CharField(label="Description", initial="Une description de vous même", widget=forms.Textarea,
                                  required=False)
    competences = forms.CharField(label="Savoir-faire",
                                  initial="Par exemple: electricien, bouturage, aromatherapie, etc...", required=False,
                                  widget=forms.Textarea)
    #avatar = forms.ImageField(required=False)
    inscrit_newsletter = forms.BooleanField(required=False)
    accepter_annuaire = forms.BooleanField(required=False)
    pseudo_june = forms.CharField(label="pseudo_june", required=False)

    #statut_adhesion = forms.ChoiceField(choices=Choix.statut_adhesion)
    #password = None

    class Meta:
        model = Profil
        fields = ['id', 'username', 'email', 'description', 'competences', 'inscrit_newsletter', 'adherent_pc',
                  'adherent_rtg', 'adherent_fer', 'adherent_scic', 'adherent_citealt', 'adherent_viure',
                  'adherent_bzz2022', 'pseudo_june', 'accepter_annuaire', 'adherent_jp', 'adherent_ssa']

    def __init__(self, *args, **kwargs):
        super(ProfilChangeForm_admin, self).__init__(*args, **kwargs)
        self.fields['description'].strip = False
        self.fields['competences'].strip = False


class ContactForm(forms.Form):
    sujet = forms.CharField(max_length=100, label="Sujet", )
    msg = forms.CharField(label="Message", widget=SummernoteWidget)
    #renvoi = forms.BooleanField(label="recevoir une copie",
     #                           help_text="Cochez si vous souhaitez obtenir une copie du mail envoyé.", required=False
     #                           )
    #captcha = CaptchaField()


class ContactMailForm(forms.Form):
    email = forms.EmailField(label="Email")
    sujet = forms.CharField(max_length=100, label="Sujet", )
    msg = forms.CharField(label="Message", widget=SummernoteWidget)
    #renvoi = forms.BooleanField(label="recevoir une copie",
    #                            help_text="Cochez si vous souhaitez obtenir une copie du mail envoyé.", required=False
    #                            )

    captcha = CaptchaField()

class CaptchaForm(forms.Form):
    captcha = CaptchaField()

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude = ['conversation', 'auteur']

        widgets = {
            'message': SummernoteWidgetWithCustomToolbar(),
        }

    def __init__(self, request, message=None, *args, **kwargs):
        super(MessageForm, self).__init__(request, *args, **kwargs)
        if message:
            self.fields['message'].initial = message


class ChercherConversationForm(forms.Form):
    destinataire = forms.ChoiceField(label='destinataire')

    def __init__(self, user, *args, **kwargs):
        super(ChercherConversationForm, self).__init__(*args, **kwargs)
        self.fields['destinataire'].choices = [(u.id, u) for i, u in
                                               enumerate(Profil.objects.all().order_by('username')) if u != user]


class MessageGeneralForm(forms.ModelForm):
    class Meta:
        model = MessageGeneral
        exclude = ['auteur', 'asso']

        widgets = {
            'message': SummernoteWidgetWithCustomToolbar(),
        }


class Message_salonForm(forms.ModelForm):
    class Meta:
        model = Message_salon
        exclude = ['auteur', 'salon']
        widgets = {
            'message': SummernoteWidget(),
        }


class Message_salonChangeForm(forms.ModelForm):
    class Meta:
        model = Message_salon
        exclude = ['auteur', 'salon']
        widgets = {
            'message': SummernoteWidget(),
        }


class MessageChangeForm(forms.ModelForm):
    class Meta:
        model = MessageGeneral
        exclude = ['auteur', 'asso']
        widgets = {
            'message': SummernoteWidget(),
        }


class InscriptionNewsletterForm(forms.ModelForm):
    class Meta:
        model = InscriptionNewsletter
        fields = ['email']


class DesInscriptionNewsletterForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = InscriptionNewsletter
        fields = ['email']


class Adhesion_permacatForm(forms.ModelForm):
    class Meta:
        model = Adhesion_permacat
        fields = '__all__'
        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def __init__(self, *args, **kwargs):
        super(Adhesion_permacatForm, self).__init__(*args, **kwargs)
        self.fields['user'].choices = [(u.id, u) for i, u in enumerate(Profil.objects.all().order_by('username')) if
                                       u.adherent_pc]


class Adhesion_assoForm(forms.ModelForm):
    class Meta:
        model = Adhesion_asso
        fields = '__all__'
        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def __init__(self, asso_slug, *args, **kwargs):
        super(Adhesion_assoForm, self).__init__(*args, **kwargs)
        self.fields['user'].choices = [(u.id, u) for i, u in enumerate(Profil.objects.all().order_by('username')) if
                                       u.estMembre_str(asso_slug)]


class nouvelleDateForm(forms.Form):
    years = [x for x in range(timezone.now().year - 3, timezone.now().year + 1)]
    date = forms.DateTimeField(initial=timezone.now(), widget=forms.SelectDateWidget(years=years))


class creerAction_articlenouveauForm(forms.Form):
    article = forms.ModelChoiceField(queryset=Article.objects.filter(estArchive=False).order_by('titre'), required=True,
                                     label="Article", )


class SalonForm(forms.ModelForm):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all().order_by("id"), required=False,)

    class Meta:
        model = Salon
        fields = ['titre', 'type_salon', 'asso', 'description', 'tags']
        widgets = {
            'description': SummernoteWidget(),
        }

    def save(self, request):
        instance = super(SalonForm, self).save(commit=False)
        instance.auteur = request.user.username
        instance.save()
        inscrit = InscritSalon(salon=instance, profil=request.user)
        inscrit.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        type_salon = cleaned_data.get("type_salon")
        asso = cleaned_data.get("asso")

        if type_salon == 2 and not asso:
            msg = _("Pour créer un salon de 'Groupe', vous devez choisir à quel Groupe il appartient ci-dessous :")
            self.add_error("asso", msg)

class Lien_AssoSalon_adminForm(forms.ModelForm):
    class Meta:
        model = Lien_AssoSalon
        fields = ['asso', 'salon',]

class SalonForm_admin(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['titre', 'type_salon', 'description', 'tags', 'slug']


class ModifierSalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['titre', 'type_salon', 'description', 'tags']
        widgets = {
            'description': SummernoteWidget(),
        }


class ModifierSalonDesciptionForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['titre', 'description', 'tags']
        widgets = {
            'description': SummernoteWidget(),
        }


class InviterDansSalonForm(forms.Form):
    profil_invite = forms.ChoiceField(label='Invité :')

    def __init__(self, salon, *args, **kwargs):
        super(InviterDansSalonForm, self).__init__(*args, **kwargs)
        if salon.type_salon == 1:
            self.fields['profil_invite'].choices = [(u.id, u) for i, u in
                                                enumerate(Profil.objects.all().order_by('username')) if
                                                not salon.est_autorise(u)]


class Profil_rechercheForm(forms.ModelForm):
    class Meta:
        model = Profil_recherche
        fields = ("profil",)
        widgets = {
            'profil': autocomplete.ModelSelect2(url='profil_ac')
        }

    def save(self):
        instance = super(Profil_rechercheForm, self).save()
        return instance


class EvenementSalonForm(forms.ModelForm):
    class Meta:
        model = EvenementSalon
        fields = ['start_time', 'titre_even', ]
        widgets = {
            'start_time': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'end_time': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def save(self, request, slug_salon):
        instance = super(EvenementSalonForm, self).save(commit=False)
        salon = Salon.objects.get(slug=slug_salon)
        instance.salon = salon
        instance.auteur = request.user
        instance.save()
        return instance


class AssocierProfil_adherentForm(forms.Form):
    adherent = forms.ModelChoiceField(queryset=Adherent.objects.all(), required=True,
                                      label="Adhérent", )

    def __init__(self, asso_slug, *args, **kwargs):
        super(AssocierProfil_adherentForm, self).__init__(*args, **kwargs)
        self.fields["adherent"].choices = [('', '(Choisir un adhérent)'), ] + [(x.id, x.nom + " " + x.prenom) for x in Adherent.objects.filter(asso__slug=asso_slug).order_by("nom", "prenom") ]


class FavorisForm(forms.ModelForm):
    class Meta:
        model = Favoris
        fields = ['nom', 'url']

    def save(self, request):
        instance = super(FavorisForm, self).save(commit=False)
        instance.profil = request.user
        instance.save()
        return instance



class FavorisFormSansUrl(forms.ModelForm):
    class Meta:
        model = Favoris
        fields = ['nom', ]

    def save(self, request, url):
        instance = super(FavorisFormSansUrl, self).save(commit=False)
        instance.url = url
        instance.profil = request.user
        instance.save()
        return instance
