from App.config import getConfiguration, setConfiguration
from plone import api

from seantis.plonetools import tests
from seantis.plonetools import utils


class TestUtils(tests.IntegrationTestCase):

    def test_get_parent(self):

        folder = self.new_temporary_folder(title='parent')
        new_type = self.new_temporary_type()

        with self.user('admin'):
            obj = api.content.create(
                id='test',
                type=new_type.id,
                container=folder
            )

        brain = utils.get_brain_by_object(obj)

        self.assertEqual(utils.get_parent(brain).title, 'parent')
        self.assertEqual(utils.get_parent(obj).title, 'parent')

        self.assertIs(type(utils.get_parent(brain)), type(brain))
        self.assertIs(type(utils.get_parent(obj)), type(obj))

    def test_in_debug_mode(self):
        cfg = getConfiguration()

        cfg.debug_mode = False
        setConfiguration(cfg)

        self.assertFalse(utils.in_debug_mode())

        cfg.debug_mode = True
        setConfiguration(cfg)

        self.assertTrue(utils.in_debug_mode())

    def test_is_existing_portal_type(self):
        new_type = self.new_temporary_type()

        self.assertTrue(utils.is_existing_portal_type(new_type.id))
        self.assertFalse(utils.is_existing_portal_type('inexistant'))

    def test_get_type_info_by_behavior(self):
        basic_behavior = 'plone.app.dexterity.behaviors.metadata.IBasic'

        basic_type = self.new_temporary_type(behaviors=[basic_behavior])
        self.new_temporary_type(behaviors=[])

        self.assertEqual(
            utils.get_type_info_by_behavior(basic_behavior), [basic_type]
        )

    def test_get_schema_from_portal_type(self):
        new_type = self.new_temporary_type()

        self.assertEqual(
            utils.get_schema_from_portal_type(new_type.id),
            new_type.lookupSchema()
        )

    def test_get_brain_by_object(self):
        with self.user('admin'):
            obj = api.content.create(
                id='test',
                type=self.new_temporary_type().id,
                container=self.new_temporary_folder()
            )

        brain = utils.get_brain_by_object(obj)
        self.assertIs(type(brain.getObject()), type(obj))
        self.assertEqual(brain.id, obj.id)

    def test_invert_dictionary(self):
        input = {
            1: 'x',
            2: 'x',
            3: 'y'
        }
        output = {
            'x': [1, 2],
            'y': [3]
        }
        self.assertEqual(utils.invert_dictionary(input), output)

    def test_add_attribute_to_metadata(self):
        catalog = api.portal.get_tool('portal_catalog')

        utils.add_attribute_to_metadata('test')
        self.assertIn('test', catalog._catalog.schema)

        # ensure that a second call doesn't do anything
        utils.add_attribute_to_metadata('test')
        self.assertIn('test', catalog._catalog.schema)

    def test_order_fields_by_schema(self):

        model = """<?xml version='1.0' encoding='utf8'?>
        <model xmlns="http://namespaces.plone.org/supermodel/schema">
            <schema>
                <field name="first" type="zope.schema.TextLine"></field>
                <field name="second" type="zope.schema.TextLine"></field>
            </schema>
        </model>"""

        schema = self.new_temporary_type(model_source=model).lookupSchema()

        self.assertEqual(
            utils.order_fields_by_schema(
                ['second', 'x', 'last', 'first'], schema
            ),
            ['first', 'second', 'x', 'last']
        )
