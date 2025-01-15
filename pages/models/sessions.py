from django.db import models
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    TabbedInterface,
    ObjectList,
)
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page, Collection
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.search import index
from wagtail.core.blocks import StreamBlock, StructBlock, RichTextBlock, ChoiceBlock
from wagtail.snippets.models import register_snippet
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from pages.models.sidebar import (
    SidebarSimpleBlock,
    SidebarHeaderBlock,
    SidebarTitleBlock,
    SidebarBorderBlock,
    SidebarImageTextBlock,
)

# Blocks
class SemesterBlock(StructBlock):
    SEMESTER_TYPE_CHOICES = [
        ('ss-2022', 'Sommersemester 2022'),
        ('ws-2022', 'Wintersemester 2022'),
        ('ss-2021', 'Sommersemester 2021'),
        ('ws-2021', 'Wintersemester 2021'),
        ('ss-2020', 'Sommersemester 2020'),
        ('ws-2020', 'Wintersemester 2020'),
        ('ss-2019', 'Sommersemester 2019'),
        ('ws-2019', 'Wintersemester 2019'),
        ('ss-2018', 'Sommersemester 2018'),
        ('ws-2018', 'Wintersemester 2018'),
    ]

    semester = ChoiceBlock(SEMESTER_TYPE_CHOICES, icon='calendar')

    class Meta:
        template = 'blocks/widgets/semester_block.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['sessions_page'] = SessionsPage.objects.first()
        context['sessions'] = SessionPage.objects.filter(semester=value['semester'])
        context['semester'] = list(filter(lambda x: x[0] == value['semester'], self.SEMESTER_TYPE_CHOICES))[0][1]
        return context

# Content Blocks
class ContentBlocks(StreamBlock):
    richtext = RichTextBlock(label="Formatierter Text")
    semester_block = SemesterBlock(label="Auflistung der Lehrveranstaltungen für ein bestimmtes Semester")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        return context

# Sidebar Blocks
class SidebarBlocks(StreamBlock):
    sidebar_title = SidebarTitleBlock(label="Grau unterlegte Überschrift")
    sidebar_header = SidebarHeaderBlock(label="Bild oben, Text darunter")
    sidebar_border = SidebarBorderBlock(label="Grau umrandeter Kasten")
    sidebar_simple = SidebarSimpleBlock(label="Schlichter Text")
    sidebar_image_text = SidebarImageTextBlock(label="Bild links, Text rechts")

class SessionsPage(RoutablePageMixin, Page):
    class Meta:
        verbose_name = 'Lehre-Seite'
        verbose_name_plural = 'Lehre-Seiten'

    content = StreamField([
        ('content', ContentBlocks(label="Hauptspalte")),
    ], block_counts={
        'content': {'min_num': 1, 'max_num': 1},
    }, verbose_name="Hauptspalte")

    sidebar = StreamField(SidebarBlocks(required=False), blank=True, verbose_name="Seitenleiste")

    content_panels = [
        FieldPanel('title'),
        FieldRowPanel([
            FieldPanel('content', classname='col8'),
            FieldPanel('sidebar', classname='col4'),
        ], classname='full')
    ]

    template = 'page.html'

    @route(r'^(?P<semester>[\w-]+)/(?P<slug>[\w-]+)/?$')
    def session_by_semester(self, request, semester, slug):
        print("semester: {}".format(semester))
        print("slug: {}".format(slug))
        session = SessionPage.objects.filter(
            semester=semester,
            slug=slug,
        ).first()
        session = get_object_or_404(
            SessionPage,
            id=session.id if session else None
        )
        return session.serve(request)

class SessionPage(Page):
    class Meta:
        verbose_name = 'Lehrveranstaltung'
        verbose_name_plural = 'Lehrveranstaltungen'

    SESSION_TYPE_CHOICES = [
        ('lecture', 'Vorlesung'),
        ('exercise', 'Übung'),
        ('study_group', 'Arbeitsgemeinschaft'),
        ('exam_prep', 'Klausurenkurs'),
        ('seminar', 'Seminar')
    ]
    SEMESTER_TYPE_CHOICES = [
        ('ss-2032', 'Sommersemester 2032'),
        ('ws-2032', 'Wintersemester 2032/33'),
        ('ss-2031', 'Sommersemester 2031'),
        ('ws-2031', 'Wintersemester 2031/32'),
        ('ss-2030', 'Sommersemester 2030'),
        ('ws-2030', 'Wintersemester 2030/31'),
        ('ss-2029', 'Sommersemester 2029'),
        ('ws-2029', 'Wintersemester 2029/30'),
        ('ss-2028', 'Sommersemester 2028'),
        ('ws-2028', 'Wintersemester 2028/29'),
        ('ss-2027', 'Sommersemester 2027'),
        ('ws-2027', 'Wintersemester 2027/28'),
        ('ss-2026', 'Sommersemester 2026'),
        ('ws-2026', 'Wintersemester 2026/27'),
        ('ss-2025', 'Sommersemester 2025'),
        ('ws-2025', 'Wintersemester 2025/26'),
        ('ss-2024', 'Sommersemester 2024'),
        ('ws-2024', 'Wintersemester 2024/25'),
        ('ss-2023', 'Sommersemester 2023'),
        ('ws-2023', 'Wintersemester 2023/24'),
        ('ss-2022', 'Sommersemester 2022'),
        ('ws-2022', 'Wintersemester 2022'),
        ('ss-2021', 'Sommersemester 2021'),
        ('ws-2021', 'Wintersemester 2021'),
        ('ss-2020', 'Sommersemester 2020'),
        ('ws-2020', 'Wintersemester 2020'),
        ('ss-2019', 'Sommersemester 2019'),
        ('ws-2019', 'Wintersemester 2019'),
        ('ss-2018', 'Sommersemester 2018'),
        ('ws-2018', 'Wintersemester 2018'),
        ('ss-2017', 'Sommersemester 2017'),
        ('ws-2017', 'Wintersemester 2017'),
        ('ss-2016', 'Sommersemester 2016'),
        ('ws-2016', 'Wintersemester 2015'),
        ('ss-2015', 'Sommersemester 2015'),
        ('ws-2015', 'Wintersemester 2014'),
        ('ss-2014', 'Sommersemester 2014'),
        ('ws-2014', 'Wintersemester 2014'),
        ('ss-2013', 'Sommersemester 2013'),
        ('ws-2013', 'Wintersemester 2013'),
        ('ss-2012', 'Sommersemester 2012'),
        ('ws-2012', 'Wintersemester 2012'),
        ('ss-2011', 'Sommersemester 2011'),
        ('ws-2011', 'Wintersemester 2011'),
        ('ss-2010', 'Sommersemester 2010'),
        ('ws-2010', 'Wintersemester 2010'),
        ('ss-2009', 'Sommersemester 2009'),
        ('ws-2009', 'Wintersemester 2009'),
        ('ss-2008', 'Sommersemester 2008'),
        ('ws-2008', 'Wintersemester 2008'),
        ('ss-2007', 'Sommersemester 2007'),
        ('ws-2007', 'Wintersemester 2007'),
        ('ss-2006', 'Sommersemester 2006'),
        ('ws-2006', 'Wintersemester 2006'),
        ('ss-2005', 'Sommersemester 2005'),
        ('ws-2005', 'Wintersemester 2005'),
        ('ss-2004', 'Sommersemester 2004'),
        ('ws-2004', 'Wintersemester 2004'),
    ]

    name = models.CharField('Name', max_length=255)
    subtitle = models.CharField('Untertitel', max_length=255)
    date = RichTextField(blank=True, verbose_name="Datum/Zeit")
    allow_comments = models.BooleanField(default=False, verbose_name="Kommentare erlaubt")
    #tags = ClusterTaggableManager(through=SessionTags, blank=True)
    speaker = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Dozent*in"
    )
    type = models.CharField(
        'Veranstaltungstyp',
        choices=SESSION_TYPE_CHOICES,
        default='lecture',
        max_length=255,
        blank=True
    )
    semester = models.CharField(
        'Semesterauswahl',
        choices=SEMESTER_TYPE_CHOICES,
        max_length=255,
        blank=True,
    )
    assessment = RichTextField(blank=True, verbose_name="Datum/Zeit")
    description = RichTextField(blank=True, verbose_name="Veranstaltungsbeschreibung")
    speaker_description = RichTextField(blank=True, verbose_name="Beschreibung des*der Dozent*in")
    material = RichTextField(blank=True, verbose_name="Materialien")
    location = RichTextField(blank=True, verbose_name="Ort")
    lat = models.FloatField(null=True, blank=True, verbose_name="Breitengrad")
    lon = models.FloatField(null=True, blank=True, verbose_name="Längengrad")

    search_fields = [
        index.SearchField('title'),
        index.SearchField('speaker'),
        index.SearchField('name'),
        index.SearchField('description'),
        index.FilterField('live'),
    ]

    sidebar = StreamField(SidebarBlocks(required=False), blank=True, verbose_name="Seitenleiste")

    content_panels = [
        FieldRowPanel([
            FieldRowPanel([
                MultiFieldPanel([
                    FieldPanel('title', classname="col12"),
                    FieldPanel('name', classname="col12"),
                    FieldPanel('subtitle', classname="col12"),
                    FieldPanel('allow_comments', classname="col12"),
                ], classname="collapsible"),
                MultiFieldPanel([
                    FieldPanel('date', classname="col12"),
                    FieldPanel('type', classname="col12"),
                    FieldPanel('semester', classname="col12"),
                    FieldPanel('description', classname="col12"),
                    FieldPanel('assessment', classname="col12"),
                ], "Info"),
                MultiFieldPanel([
                    FieldPanel('speaker', classname="col12"),
                    FieldPanel('speaker_description', classname="col12"),
                ], "Speaker"),
                MultiFieldPanel([
                    FieldPanel('location', classname="col12"),
                    FieldPanel('lat', classname="col6"),
                    FieldPanel('lon', classname="col6"),
                ], "Location"),
                MultiFieldPanel([
                    FieldPanel('material', classname="col12"),
                ], classname="collapsible"),
            ], classname='session-content d-flex flex-column col8'),
            FieldRowPanel([
                FieldPanel('sidebar', classname='full'),
            ], classname='session-sidebar d-flex flex-column col4')
        ])
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings', classname='settings'),
    ])

    #parent_page_types = [SessionsPage]

    #template = 'page.html'

    @property
    def sessions_page(self):
        return self.get_parent().specific

    def get_absolute_url(self):
        return self.get_url()

    def get_context(self, request):
        context = super().get_context(request)
        context['request'] = request
        context['semester'] = list(filter(lambda x: x[0] == self.semester, self.SEMESTER_TYPE_CHOICES))[0][1]
        return context

    def author_name(self):
        return "{} {}".format(self.author.first_name, self.author.last_name)

    parent_page_types = [SessionsPage]

    content_panels = Page.content_panels #+ [
        #FieldPanel('author'),
        #MultiFieldPanel([
        #    FieldPanel('date'),
        #    FieldPanel('tags')
        #], heading="Article information"),
        #FieldPanel('body', classname='full'),
    #]

    template = 'pages/lehre_session_page.html'
