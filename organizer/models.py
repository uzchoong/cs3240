import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
import os
from django.conf import settings
from .tasks import send_reminder_email
from datetime import timedelta
from django.core import serializers


# https://docs.djangoproject.com/en/3.2/ref/models/fields/
# https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-the-existing-user-model
# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
# https://www.revsys.com/tidbits/tips-using-djangos-manytomanyfield/

# run migrations later
# follow Django docs, have User page show Profile fields

# add major field (text/char field), to-do list and calendar (models)
# https://career.virginia.edu/explore/majors

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    computingID = models.CharField(max_length=10, blank=False, verbose_name="Computing ID")

    AERO = 'AE'
    AF_AM_STUDIES = 'AAS'
    AM_STUDIES = 'AMST'
    ANTHRO = 'ANTH'
    APL_STATS = 'APST'
    ARCHAEOLOGY = 'ARCY'
    ARCH_HIST = 'ARH'
    ARCH = 'ARCH'
    ASTRO = 'ASTR'
    ASTRO_PHYS = 'ASTROPHYS'
    INTER_ST = 'BIS'
    PROF_ST_HSM = 'BPHM'
    BIO = 'BIOL'
    BIOMED = 'BME'
    CHEM = 'CHEM'
    CHEM_ENG = 'CHE'
    CIVIL = 'CE'
    CLASSICS = 'CLAS'
    COG_SCI = 'COGS'
    COMMERCE = 'COMM'
    COMP_LIT = 'CPLT'
    COMP_ENG = 'CPE'
    CS_BA = 'BACS'
    CS_BS = 'BSCS'
    DRAMA = 'DRAM'
    EARLY_CHILD_ED = 'ECED'
    E_A_ST = 'EAST'
    ECON = 'ECON'
    ELEC_ENG = 'EE'
    ELEM_ED = 'ELED'
    ENG_SCI = 'ESCI'
    ENGLISH = 'ENGL'
    ENV_SCI = 'EVSC'
    ENV_TH_PR = 'ETP'
    TEACHER = 'TEACH'
    FRENCH = 'FREN'
    GERMAN = 'GERM'
    GERM_ST = 'GEST'
    GLOBAL_ST = 'GLST'
    HISTORY = 'HIST'
    ART_HIST = 'ARTH'
    HUMAN_BIO = 'HBIO'
    JEWISH_ST = 'JWST'
    KINESIOLOGY = 'KINE'
    LAT_AM_ST = 'LAST'
    LING = 'LING'
    MAT_SCI_ENG = 'MSE'
    MATH = 'MATH'
    MECH = 'ME'
    MEDIA_ST = 'MDST'
    MEDIEVAL_ST = 'MSP'
    M_E_S_A_LANG_CUL = 'MESA'
    MUSIC = 'MUSI'
    NEURO = 'NEUR'
    NURSING = 'NURS'
    PHIL = 'PHIL'
    PHYSICS = 'PHYS'
    POL_SOC_THT = 'PST'
    POL_PHIL_POL_LAW = 'PPL'
    POLITICS = 'POLI'
    PSYCH = 'PSYC'
    RELG_ST = 'RELG'
    SLAV_LA_LIT = 'SLAV'
    SOCIOLOGY = 'SOC'
    SPANISH = 'SPAN'
    SPC_ED = 'EDIS'
    SPH_COM_DIS = 'SCDI'
    STAT = 'STAT'
    STUD_ART = 'ARTS'
    SYS_ENG = 'SYS'
    URB_ENV_PLAN = 'PLAN'
    WGS = 'WGS'
    Y_SOC_INN = 'YSIN'
    UNDECLARED = '____'

    MAJOR_CHOICES = [
        (AERO, 'Aerospace Engineering'),
        (AF_AM_STUDIES, 'African American and African Studies'),
        (AM_STUDIES, 'American Studies'),
        (ANTHRO, 'Anthropology'),
        (APL_STATS, 'Applied Statistics'),
        (ARCHAEOLOGY, 'Archaeology'),
        (ARCH_HIST, 'Architectural History'),
        (ARCH, 'Architecture'),
        (ASTRO, 'Astronomy'),
        (ASTRO_PHYS, 'Astronomy-Physics'),
        (INTER_ST, 'Interdisciplinary Studies'),
        (PROF_ST_HSM, 'Professional Studies in Health Sciences Management'),
        (BIO, 'Biology'),
        (BIOMED, 'Biomedical Engineering'),
        (CHEM, 'Chemistry'),
        (CHEM_ENG, 'Chemical Engineering'),
        (CIVIL, 'Civil Engineering'),
        (CLASSICS, 'Classics'),
        (COG_SCI, 'Cognitive Science'),
        (COMMERCE, 'Commerce'),
        (COMP_LIT, 'Comparative Literature'),
        (COMP_ENG, 'Computer Engineering'),
        (CS_BA, 'Computer Science, BA'),
        (CS_BS, 'Computer Science, BS'),
        (DRAMA, 'Drama'),
        (EARLY_CHILD_ED, 'Early Childhood Education'),
        (E_A_ST, 'East Asian Studies'),
        (ECON, 'Economics'),
        (ELEC_ENG, 'Electrical Engineering'),
        (ELEM_ED, 'Elementary Education'),
        (ENG_SCI, 'Engineering Science'),
        (ENGLISH, 'English'),
        (ENV_SCI, 'Environmental Sciences'),
        (ENV_TH_PR, 'Environmental Thought and Practice'),
        (TEACHER, 'Five-Year Teacher Education Program'),
        (FRENCH, 'French'),
        (GERMAN, 'German'),
        (GERM_ST, 'German Studies'),
        (GLOBAL_ST, 'Global Studies'),
        (HISTORY, 'History'),
        (ART_HIST, 'History of Art'),
        (HUMAN_BIO, 'Human Biology'),
        (JEWISH_ST, 'Jewish Studies'),
        (KINESIOLOGY, 'Kinesiology'),
        (LAT_AM_ST, 'Latin American Studies'),
        (LING, 'Linguistics'),
        (MAT_SCI_ENG, 'Materials Science and Engineering'),
        (MATH, 'Mathematics'),
        (MECH, 'Mechanical Engineering'),
        (MEDIA_ST, 'Media Studies'),
        (MEDIEVAL_ST, 'Medieval Studies'),
        (M_E_S_A_LANG_CUL, 'Middle Eastern and South Asian Languages and Cultures'),
        (MUSIC, 'Music'),
        (NEURO, 'Neuroscience'),
        (NURSING, 'Nursing'),
        (PHIL, 'Philosophy'),
        (PHYSICS, 'Physics'),
        (POL_SOC_THT, 'Political and Social Thought'),
        (POL_PHIL_POL_LAW, 'Political Philosophy, Policy, and Law'),
        (POLITICS, 'Politics'),
        (PSYCH, 'Psychology'),
        (RELG_ST, 'Religious Studies'),
        (SLAV_LA_LIT, 'Slavic Languages and Literatures'),
        (SOCIOLOGY, 'Sociology'),
        (SPANISH, 'Spanish'),
        (SPC_ED, 'Special Education'),
        (SPH_COM_DIS, 'Speech Communication Disorders'),
        (STAT, 'Statistics'),
        (STUD_ART, 'Studio Art'),
        (SYS_ENG, 'Systems Engineering'),
        (URB_ENV_PLAN, 'Urban and Environmental Planning'),
        (WGS, 'Women, Gender, & Sexuality'),
        (Y_SOC_INN, 'Youth & Social Innovation'),
        (UNDECLARED, 'Undeclared')
    ]
    major = models.CharField(max_length=100, choices=MAJOR_CHOICES, blank=True)

# signals automatically create/update Profile model when User instances are created/updated
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# https://docs.djangoproject.com/en/3.2/ref/validators/#built-in-validators
# https://stackoverflow.com/questions/30849862/django-max-length-for-integerfield
class Classes(models.Model):
    name = models.CharField(max_length=200, verbose_name="Course Name")
    credits = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(6)])

    ACCT = 'ACCT'
    AERO = 'AE'
    AF_AM_STUDIES = 'AAS'
    AIRS = 'AIRS'
    AM_STUDIES = 'AMST'
    ANTHRO = 'ANTH'
    APL_STATS = 'APST'
    APMA = 'APMA'
    AR_AD = 'ARAD'
    ARAB = 'ARAB'
    ARCH = 'ARCH'
    ARCH_HIST = 'ARH'
    ARCHAEOLOGY = 'ARCY'
    ART_HIST = 'ARTH'
    ASL = 'ASL'
    ASTRO = 'ASTR'
    BIO = 'BIOL'
    BIOMED = 'BME'
    CH_TR = 'CHTR'
    CHEM = 'CHEM'
    CHEM_ENG = 'CHE'
    CHIN = 'CHIN'
    CIVIL = 'CE'
    CLASSICS = 'CLAS'
    COG_SCI = 'COGS'
    COMMERCE = 'COMM'
    COMP_ENG = 'CPE'
    COMP_LIT = 'CPLT'
    CREO = 'CREO'
    CS = 'CS'
    DANC = 'DANC'
    DRAMA = 'DRAM'
    DS = 'DS'
    E_A_ST = 'EAST'
    EALC = 'EALC'
    EARLY_CHILD_ED = 'ECED'
    ECE = 'ECE'
    ECON = 'ECON'
    ED_HS = 'EDHS'
    ED_LF = 'EDLF'
    EGMT = 'EGMT'
    ELEC_ENG = 'EE'
    ELEM_ED = 'ELED'
    ENCW = 'ENCW'
    ENG_SCI = 'ESCI'
    ENGLISH = 'ENGL'
    ENGR = 'ENGR'
    ENTP = 'ENTP'
    ENV_SCI = 'EVSC'
    ENV_TH_PR = 'ETP'
    ENWR = 'ENWR'
    ESL = 'ESL'
    EV_AT = 'EVAT'
    EV_EC = 'EVEC'
    EV_GE = 'EVGE'
    EV_HY = 'EVHY'
    FR_TR = 'FRTR'
    FRENCH = 'FREN'
    GDS = 'GDS'
    GE_TR = 'GETR'
    GERM_ST = 'GEST'
    GERMAN = 'GERM'
    GLOBAL_ST = 'GLST'
    GREE = 'GREE'
    GSGS = 'GSDS'
    GSSJ = 'GSSJ'
    GSVS = 'GSVS'
    HEBR = 'HEBR'
    HI_AF = 'HIAF'
    HI_EA = 'HIEA'
    HI_EU = 'HIEU'
    HI_LA = 'HILA'
    HI_ME = 'HIME'
    HI_SA = 'HISA'
    HI_US = 'HIUS'
    HIND = 'HIND'
    HISTORY = 'HIST'
    HUMAN_BIO = 'HBIO'
    INST = 'INST'
    INTER_ST = 'BIS'
    IT_TR = 'ITTR'
    ITAL = 'ITAL'
    JAPN = 'JAPN'
    JEWISH_ST = 'JWST'
    JP_TR = 'JPTR'
    KICH = 'KICH'
    KINESIOLOGY = 'KINE'
    KOR = 'KOR'
    LAT_AM_ST = 'LAST'
    LATI = 'LATI'
    LING = 'LING'
    M_E_S_A_LANG_CUL = 'MESA'
    MAE = 'MAE'
    MAT_SCI_ENG = 'MSE'
    MATH = 'MATH'
    MECH = 'ME'
    MEDIA_ST = 'MDST'
    MEDIEVAL_ST = 'MSP'
    MEST = 'MEST'
    MU_BD = 'MUBD'
    MU_EN = 'MUEN'
    MU_PF = 'MUPF'
    MUSIC = 'MUSI'
    NEURO = 'NEUR'
    NUCO = 'NUCO'
    NURSING = 'NURS'
    PE_TR = 'PETR'
    PERS = 'PERS'
    PHIL = 'PHIL'
    PHS = 'PHS'
    PHS = 'PHS'
    PHYSICS = 'PHYS'
    PLAD = 'PLAD'
    PLAP = 'PLAP'
    PLCP = 'PLCP'
    PLIR = 'PLIR'
    PLPT = 'PLPT'
    POL = 'POL'
    POL_PHIL_POL_LAW = 'PPL'
    POL_SOC_THT = 'PST'
    POLITICS = 'POLI'
    PORT = 'PORT'
    PROF_ST_HSM = 'BPHM'
    PSYCH = 'PSYC'
    REL_A = 'RELA'
    REL_B = 'RELB'
    REL_C = 'RELC'
    REL_H = 'RELH'
    REL_I = 'RELI'
    REL_J = 'RELJ'
    RELG_ST = 'RELG'
    RU_TR = 'RUTR'
    RUSS = 'RUSS'
    SANS = 'SANS'
    SAST = 'SAST'
    SLAV_LA_LIT = 'SLAV'
    SLFK = 'SLFK'
    SOCIOLOGY = 'SOC'
    SPANISH = 'SPAN'
    SPC_ED = 'EDIS'
    SPH_COM_DIS = 'SCDI'
    STAT = 'STAT'
    STS = 'STS'
    STUD_ART = 'ARTS'
    SWAH = 'SWAH'
    SYS_ENG = 'SYS'
    URB_ENV_PLAN = 'PLAN'
    URDU = 'URDU'
    USEM = 'USEM'
    WGS = 'WGS'
    Y_SOC_INN = 'YSIN'

    DEPARTMENT_CHOICES = [
        (ACCT, 'Accounting'),
        (AERO, 'Aerospace Engineering'),
        (AF_AM_STUDIES, 'African American and African Studies'),
        (AIRS, 'Air Science'),
        (AM_STUDIES, 'American Studies'),
        (ANTHRO, 'Anthropology'),
        (APL_STATS, 'Applied Statistics'),
        (APMA, 'Applied Mathematics'),
        (ARAB, 'Arabic'),
        (ARCH, 'Architecture'),
        (ARCHAEOLOGY, 'Archaeology'),
        (ARCH_HIST, 'Architectural History'),
        (ART_HIST, 'Art History'),
        (AR_AD, 'Arts Administration'),
        (ASL, 'American Sign Language'),
        (ASTRO, 'Astronomy'),
        (BIO, 'Biology'),
        (BIOMED, 'Biomedical Engineering'),
        (CHEM, 'Chemistry'),
        (CHEM_ENG, 'Chemical Engineering'),
        (CHIN, 'Chinese'),
        (CH_TR, 'Chinese in Translation'),
        (CIVIL, 'Civil Engineering'),
        (CLASSICS, 'Classics'),
        (COG_SCI, 'Cognitive Science'),
        (COMMERCE, 'Commerce'),
        (COMP_LIT, 'Comparative Literature'),
        (COMP_ENG, 'Computer Engineering'),
        (CS, 'Computer Science'),
        (CREO, 'Creole'),
        (DANC, 'Dance'),
        (DRAMA, 'Drama'),
        (DS, 'Data Science'),
        (EALC, 'East Asian Languages, Literatures, and Cultures'),
        (EARLY_CHILD_ED, 'Early Childhood Education'),
        (ECE, 'Electrical and Computer Engineering'),
        (ECON, 'Economics'),
        (ED_HS, 'Education-Human Services'),
        (ED_LF, 'Education-Leadership, Foundations, and Policy'),
        (EGMT, 'Engagement'),
        (ELEC_ENG, 'Electrical Engineering'),
        (ELEM_ED, 'Elementary Education'),
        (ENCW, 'Creative Writing'),
        (ENGLISH, 'English'),
        (ENGR, 'Engineering'),
        (ENG_SCI, 'Engineering Science'),
        (ENTP, 'Entrepreneurship'),
        (ENV_SCI, 'Environmental Sciences'),
        (ENV_TH_PR, 'Environmental Thought and Practice'),
        (ENWR, 'Writing and Rhetoric'),
        (ESL, 'English as a Second Lanaguge'),
        (EV_AT, 'Environmental Sciences-Atmospheric Sciences'),
        (EV_EC, 'Environmental Sciences-Ecology'),
        (EV_GE, 'Environmental Sciences-Geosciences'),
        (EV_HY, 'Environmental Sciences-Hydrolgy'),
        (E_A_ST, 'East Asian Languages, Literatures, and Culture'),
        (FRENCH, 'French'),
        (FR_TR, 'French in Translation'),
        (GDS, 'Global Development Studies'),
        (GERMAN, 'German'),
        (GERM_ST, 'German Studies'),
        (GE_TR, 'German in Translation'),
        (GLOBAL_ST, 'Global Studies'),
        (GREE, 'Greek'),
        (GSGS, 'Global Studies-Global Studies'),
        (GSSJ, 'Global Studies-Security and Justice'),
        (GSVS, 'Global Studies-Environments and Sustainability'),
        (HEBR, 'Hebrew'),
        (HIND, 'Hindi'),
        (HISTORY, 'History'),
        (HI_AF, 'History-African History'),
        (HI_EA, 'History-East Asian History'),
        (HI_EU, 'History-European History'),
        (HI_LA, 'History-Latin American History'),
        (HI_ME, 'History-Middle Eastern History'),
        (HI_SA, 'History-South Asian History'),
        (HI_US, 'History-United States History'),
        (HUMAN_BIO, 'Human Biology'),
        (INST, 'Interdisciplinary Studies'),
        (INTER_ST, 'Interdisciplinary Studies'),
        (ITAL, 'Italian'),
        (IT_TR, 'Italian in Translation'),
        (JAPN, 'Japanese'),
        (JEWISH_ST, 'Jewish Studies'),
        (JP_TR, 'Japanese in Translation'),
        (KICH, 'Maya Kiche'),
        (KINESIOLOGY, 'Kinesiology'),
        (KOR, 'Korean'),
        (LATI, 'Latin'),
        (LAT_AM_ST, 'Latin American Studies'),
        (LING, 'Linguistics'),
        (MAE, 'Mechanical & Aerospace Engineering'),
        (MATH, 'Mathematics'),
        (MAT_SCI_ENG, 'Materials Science and Engineering'),
        (MECH, 'Mechanical Engineering'),
        (MEDIA_ST, 'Media Studies'),
        (MEDIEVAL_ST, 'Medieval Studies'),
        (MEST, 'Middle Eastern Studies'),
        (MUSIC, 'Music'),
        (MU_BD, 'Music-Marching Band'),
        (MU_EN, 'Music-Ensembles'),
        (MU_PF, 'Music-Private Performance Instruction'),
        (M_E_S_A_LANG_CUL, 'Middle Eastern and South Asian Languages and Cultures'),
        (NEURO, 'Neuroscience'),
        (NUCO, 'Nursing Core'),
        (NURSING, 'Nursing'),
        (PERS, 'Persian'),
        (PE_TR, 'Persian in Translation'),
        (PHIL, 'Philosophy'),
        (PHS, 'Public Health Sciences'),
        (PHS, 'Public Health Sciences'),
        (PHYSICS, 'Physics'),
        (PLAD, 'Politics-Departmental Seminar'),
        (PLAP, 'Politics-American Politics'),
        (PLCP, 'Politics-Comparative Politics'),
        (PLIR, 'Politics-International Relations'),
        (PLPT, 'Politics-Political Theory'),
        (POL, 'Polish'),
        (POLITICS, 'Politics'),
        (POL_PHIL_POL_LAW, 'Political Philosophy, Policy, and Law'),
        (POL_SOC_THT, 'Political and Social Thought'),
        (PORT, 'Portuguese'),
        (PROF_ST_HSM, 'Professional Studies in Health Sciences Management'),
        (PSYCH, 'Psychology'),
        (RELG_ST, 'Religious Studies'),
        (REL_A, 'Religion-African Religions'),
        (REL_B, 'Religion-Buddhism'),
        (REL_C, 'Religion-Christianity'),
        (REL_H, 'Religion-Hinduism'),
        (REL_I, 'Religion-Islam'),
        (REL_J, 'Religion-Judaism'),
        (RUSS, 'Russian'),
        (RU_TR, 'Russian in Translation'),
        (SANS, 'Sanskrit'),
        (SAST, 'South Asian Studies'),
        (SLAV_LA_LIT, 'Slavic Languages and Literatures'),
        (SLFK, 'Slavic Folklore & Oral Literature'),
        (SOCIOLOGY, 'Sociology'),
        (SPANISH, 'Spanish'),
        (SPC_ED, 'Special Education'),
        (SPH_COM_DIS, 'Speech Communication Disorders'),
        (STAT, 'Statistics'),
        (STS, 'Science, Technology, and Society'),
        (STUD_ART, 'Studio Art'),
        (SWAH, 'Swahili'),
        (SYS_ENG, 'Systems Engineering'),
        (URB_ENV_PLAN, 'Urban and Environmental Planning'),
        (URDU, 'Urdu'),
        (USEM, 'University Seminar'),
        (WGS, 'Women, Gender, & Sexuality'),
        (Y_SOC_INN, 'Youth & Social Innovation')
    ]

    code = models.CharField(max_length=4, choices=DEPARTMENT_CHOICES, blank=False, verbose_name="Department")
    courseNumber = models.CharField(max_length=4, validators=[RegexValidator(r'^\d{1,10}$')],
                                    verbose_name="Course Number")  # ensure only integers are accepted
    year = models.IntegerField(default=2021, validators=[MinValueValidator(2000)])  # change default??
    professor = models.CharField(max_length=200, default='Staff')

    user = models.ManyToManyField(User)

    # https://docs.djangoproject.com/en/3.2/ref/models/constraints/#django.db.models.UniqueConstraint
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['code', 'courseNumber', 'professor', 'year'],
                                    name='unique-class')
        ]
        ordering = ('name',)

    def __str__(self):
        return self.code + " " + str(self.courseNumber) + " - " + self.professor


class Calendar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # add more ...


class ToDo(models.Model):
    title = models.CharField(max_length=250)  # the title for the toDo item
    content = models.TextField(blank=True)  # the text for the toDo item
    created = models.DateTimeField(auto_now_add=True)  # the date created
    dueDate = models.DateTimeField(default=(timezone.now() + timedelta(minutes=30)))  # the due date for the assignment

    TEN_MIN = 10
    FIFTEEN_MIN = 15
    THIRTY_MIN = 30
    FORTYFIVE_MIN = 45
    ONE_HOUR = 60
    ONE_HOUR_FIFTEEN_MIN = 75
    ONE_HOUR_THIRTY_MIN = 90
    TWO_HOUR = 120
    THREE_HOUR = 180
    FOUR_HOUR = 240
    FIVE_HOUR = 300
    SIX_HOUR = 360
    SEVEN_HOUR = 420
    EIGHT_HOUR = 480
    NINE_HOUR = 540
    TEN_HOUR = 600
    ELEVEN_HOUR = 660
    TWELVE_HOUR = 720
    SIXTEEN_HOUR = 960
    TWENTY_HOUR = 1200
    ONE_DAY = 1440
    TWO_DAY = 2880
    THREE_DAY = 4320
    FOUR_DAY = 5760
    FIVE_DAY = 7200
    SIX_DAY = 8640
    ONE_WEEK = 10080

    REMINDTIME_CHOICES = [
        (TEN_MIN, '10 min'),
        (FIFTEEN_MIN, '15 min'),
        (THIRTY_MIN, '30 min'),
        (FORTYFIVE_MIN, '45 min'),
        (ONE_HOUR, '1 hour'),
        (ONE_HOUR_FIFTEEN_MIN, '1 hour 15 min'),
        (ONE_HOUR_THIRTY_MIN, '1 hour 30 min'),
        (TWO_HOUR, '2 hours'),
        (THREE_HOUR, '3 hours'),
        (FOUR_HOUR, '4 hours'),
        (FIVE_HOUR, '5 hours'),
        (SIX_HOUR, '6 hours'),
        (SEVEN_HOUR, '7 hours'),
        (EIGHT_HOUR, '8 hours'),
        (NINE_HOUR, '9 hours'),
        (TEN_HOUR, '10 hours'),
        (ELEVEN_HOUR, '11 hours'),
        (TWELVE_HOUR, '12 hours'),
        (SIXTEEN_HOUR, '16 hours'),
        (TWENTY_HOUR, '20 hours'),
        (ONE_DAY, '1 day'),
        (TWO_DAY, '2 days'),
        (THREE_DAY, '3 days'),
        (FOUR_DAY, '4 days'),
        (FIVE_DAY, '5 days'),
        (SIX_DAY, '6 days'),
        (ONE_WEEK, '1 week')
    ]
    remindTime = models.IntegerField(choices=REMINDTIME_CHOICES, default=TEN_MIN)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('dueDate',)

    def __str__(self):
        return self.title


# https://stackoverflow.com/questions/55324117/django-signal-based-on-the-datetime-field-value/55328013
# https://stackoverflow.com/questions/55337206/update-tasks-in-celery-with-rabbitmq/55337663#55337663
# https://docs.djangoproject.com/en/3.2/topics/signals/
# https://docs.djangoproject.com/en/3.2/ref/signals/
# https://stackoverflow.com/questions/2391002/django-serializer-for-one-object
@receiver(post_save, sender=ToDo)
def reminder_todo_10min(instance, *args, **kwargs):
    data = serializers.serialize("json", [ToDo.objects.get(id=instance.id)])
    just_the_object = data[1:-1]
    # print(just_the_object) #for testing
    email = instance.user.email
    # print(instance.dueDate) #for testing

    ##
    # add functionality to be able to change when the reminder is sent
    ##
    timeToRemind = instance.dueDate - timedelta(minutes=instance.remindTime)
    secondsUntilRemind = (timeToRemind - timezone.now()).seconds
    # send_reminder_email.apply_async((just_the_object, email), countdown=secondsUntilRemind)  # with countdown
    send_reminder_email.apply_async((just_the_object, email), eta=timeToRemind)  # with eta


# https://www.askpython.com/django/upload-files-to-django
class Note(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='notes/')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    theClass = models.ForeignKey(Classes, on_delete=models.CASCADE)

    isVisible = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title}"

    @property
    def filename(self):
        return os.path.basename(self.file.name)
        # return os.path.splitext(file.name)[0]

    # https://stackoverflow.com/questions/17663809/deleting-uploaded-files-in-django
    def delete(self, *args, **kwargs):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))
        except FileNotFoundError:
            pass
        finally:
            super(Note, self).delete(*args, **kwargs)

    @property
    def code(self):
        return self.theClass.code

