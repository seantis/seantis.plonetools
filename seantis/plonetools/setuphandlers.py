import logging
from Products.CMFCore.utils import getToolByName


def get_sane_index_handler_and_step(module, wanted):
    """ DRY version of the following:
    http://maurits.vanrees.org/weblog/archive/2009/12/catalog

    1. Create your-module.default.txt in your profiles/default

    2. Add an instance to your setuphandler.py, providing your module name
    and the list of wanted indexes.

    e.g.
        add_catalog_indexes, import_indexes = get_sane_index_handler_and_step(
            'seantis.people', [
                ('first_letter', 'FieldIndex')
            ]
        )

    3. Add your own import step to your configure.zcml

    e.g.
        <!-- Import step for indexes -->
        <genericsetup:importStep
            name="seantis.people"
            description=""
            title="seantis.people indexes"
            handler="seantis.people.setuphandler.import_indexes"
        />

    """

    def add_catalog_indexes(context, logger=None):
        """Method to add our wanted indexes to the portal_catalog.

        @parameters:

        When called from the import_various method below, 'context' is
        the plone site and 'logger' is the portal_setup logger.  But
        this method can also be used as upgrade step, in which case
        'context' will be portal_setup and 'logger' will be None.

        """

        logger = logger or logging.getLogger(module)

        # Run the catalog.xml step as that may have defined new metadata
        # columns.  We could instead add <depends name="catalog"/> to
        # the registration of our import step in zcml, but doing it in
        # code makes this method usable as upgrade step as well.  Note that
        # this silently does nothing when there is no catalog.xml, so it
        # is quite safe.
        setup = getToolByName(context, 'portal_setup')
        setup.runImportStepFromProfile(
            'profile-{}:default'.format(module), 'catalog'
        )

        catalog = getToolByName(context, 'portal_catalog')
        indexes = catalog.indexes()

        indexables = []
        for name, meta_type in wanted:
            if name not in indexes:
                catalog.addIndex(name, meta_type)
                indexables.append(name)
                logger.info("Added %s for field %s.", meta_type, name)

        if indexables:
            logger.info("Indexing new indexes %s.", ', '.join(indexables))
            catalog.manage_reindexIndex(ids=indexables)

    def import_indexes(context):
        """Import step for configuration that is not handled in xml files.
        """
        # Only run step if a flag file is present
        if context.readDataFile('{}-default.txt'.format(module)) is None:
            return

        site = context.getSite()
        add_catalog_indexes(site, context.getLogger(module))

    return add_catalog_indexes, import_indexes
