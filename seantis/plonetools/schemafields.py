import logging
log = logging.getLogger('seantis.plonetools')

import colour
import stdnum.ch.ssn
import stdnum.iban

from urlparse import urlparse
from zope.schema import TextLine, URI
from zope.schema.interfaces import InvalidURI

from zope.interface import Invalid

from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid

from seantis.plonetools import _


class Email(TextLine):

    def __init__(self, *args, **kwargs):
        super(TextLine, self).__init__(*args, **kwargs)

    def _validate(self, value):
        super(TextLine, self)._validate(value)
        validate_email(value)


class Website(URI):
    """URI field which assumes http:// if no protocol is specified."""

    def fromUnicode(self, value):
        try:
            if not urlparse(value).scheme:
                value = u'http://' + value
        except:
            log.exception('invalid url %s' % value)
            raise InvalidURI(value)

        return super(Website, self).fromUnicode(value)


class HexColor(TextLine):

    def __init__(self, *args, **kwargs):
        super(TextLine, self).__init__(*args, **kwargs)

    def _validate(self, value):
        super(TextLine, self)._validate(value)
        validate_hex_color(value)


class IBAN(TextLine):

    def __init__(self, *args, **kwargs):
        super(TextLine, self).__init__(*args, **kwargs)

    def _validate(self, value):
        super(TextLine, self)._validate(value)
        validate_iban(value)


class SwissSocialSecurityNumber(TextLine):

    def __init__(self, *args, **kwargs):
        super(TextLine, self).__init__(*args, **kwargs)

    def _validate(self, value):
        super(TextLine, self)._validate(value)
        validate_swiss_ssn(value)


def validate_email(value):
    try:
        email = (value or u'').strip()
        if email:
            checkEmailAddress(email)
    except EmailAddressInvalid:
        raise Invalid(_(u"Invalid email address: {}".format(email)))

    return True


def validate_hex_color(value):
    try:
        color = (value or u'').strip()
        if color:
            colour.Color(value)
    except (ValueError, AttributeError):
        raise Invalid(_(u"Invalid hex color: {}".format(color)))

    return True


def validate_iban(value):
    iban = (value or u'').strip()

    if iban and not stdnum.iban.is_valid(iban):
        raise Invalid(_(u"Invalid IBAN number: {}".format(iban)))

    return True


def validate_swiss_ssn(value):
    ssn = (value or u'').strip()

    if ssn and not stdnum.ch.ssn.is_valid(ssn):
        raise Invalid(_(u"Invalid Swiss Social Security number: {}".format(
            ssn
        )))

    return True


# optional plone.schemaeditor integration
try:
    from plone.schemaeditor.fields import FieldFactory
    EmailFactory = FieldFactory(Email, _(u"Email"))
    WebsiteFactory = FieldFactory(Website, _(u"Website"))
    HexColorFactory = FieldFactory(HexColor, _(u"Color"))
    IBANFactory = FieldFactory(IBAN, _(u"IBAN"))
    SwissSocialSecurityNumberFactory = FieldFactory(
        SwissSocialSecurityNumber, _(u"Swiss Social Security Number")
    )
except ImportError:
    pass


# optional plone.supermodel integration
try:
    from plone.supermodel.exportimport import BaseHandler
    EmailHandler = BaseHandler(Email)
    WebsiteHandler = BaseHandler(Website)
    HexColorHandler = BaseHandler(HexColor)
    IBANHandler = BaseHandler(IBAN)
    SwissSocialSecurityNumberHandler = BaseHandler(SwissSocialSecurityNumber)
except ImportError:
    pass
