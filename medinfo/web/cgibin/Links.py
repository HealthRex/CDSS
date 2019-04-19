#!/usr/bin/env python
"""Just a bunch of constant lists as a common references
for the NAV and footer links throughout the site.
"""

APP_BASE = '/'

HEADER_LINK_FORMAT = '<a class="breadcrumb" href="%s" target="_top">%s</a>'
HEADER_LINK_SEPARATOR = ' / '

NAV_LINK_FORMAT = '<td><a href="%s" target="_top">%s</a></td>'
NAV_LINK_SEPARATOR = '<td width=1 class="line"></td>'

FOOTER_LINK_FORMAT = '<a href="%s">%s</a>'
FOOTER_LINK_SEPARATOR = ' | '

def buildLinks( linkHRefList, linkTextList, linkFormat, linkSeparator ):
    """Given a list of link hrefs and text, build a single formatted HTML string
    to represent all of them as a set of navigation links.
    """
    navLinks = [];
    for href, text in zip(linkHRefList,linkTextList):
        navLinks.append(linkFormat % (href,text))
        navLinks.append(linkSeparator)
    navLinks[-1] = "" # Eliminate last separator, but ensure get newline at end
    navLinks = str.join("\n",navLinks)
    return navLinks;


################## Base Navigation Links ##########################
BASE_LINK_DIR = "..";

HEADER_LINK_HREF = [];  HEADER_LINK_TEXT = [];
HEADER_LINK_HREF.append("../../index.htm");        HEADER_LINK_TEXT.append("MedInfo");
HEADER_LINKS = buildLinks(HEADER_LINK_HREF,HEADER_LINK_TEXT,HEADER_LINK_FORMAT,HEADER_LINK_SEPARATOR);

NAV_LINK_HREF = [];                                 NAV_LINK_TEXT = [];
NAV_LINK_HREF.append("../../index.htm");               NAV_LINK_TEXT.append("Home")
NAV_LINK_HREF.append("../../cgibin/cpoe/ItemRecommenderWeb.py");       NAV_LINK_TEXT.append("Item Recommender")
NAV_LINK_HREF.append("../../cgibin/admin/DBUtilWeb.py");           NAV_LINK_TEXT.append("DBUtil")
NAV_LINKS = buildLinks(NAV_LINK_HREF,NAV_LINK_TEXT,NAV_LINK_FORMAT,NAV_LINK_SEPARATOR);

FOOTER_LINK_HREF = [];                                  FOOTER_LINK_TEXT = [];
FOOTER_LINK_HREF.append("../../index.htm");                FOOTER_LINK_TEXT.append("Home");
FOOTER_LINK_HREF.append("../../contacts.htm");             FOOTER_LINK_TEXT.append("Contacts");
FOOTER_LINKS = buildLinks(FOOTER_LINK_HREF,FOOTER_LINK_TEXT,FOOTER_LINK_FORMAT,FOOTER_LINK_SEPARATOR);

############### Admin Nav Links #################################
ADMIN_HEADER_LINKS = HEADER_LINKS;
ADMIN_NAV_LINKS = NAV_LINKS;
ADMIN_FOOTER_LINKS = FOOTER_LINKS;
