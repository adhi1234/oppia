# coding: utf-8
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Jeremy Emerson'

import unittest

from core.domain import widget_domain
from extensions.objects.models import objects
import feconf
import test_utils


class AnswerHandlerUnitTests(test_utils.GenericTestBase):
    """Test the AnswerHandler domain object."""

    def test_rules_property(self):
        """Test that answer_handler.rules behaves as expected."""
        answer_handler = widget_domain.AnswerHandler()
        self.assertEqual(answer_handler.name, 'submit')
        self.assertEqual(answer_handler.rules, [])

        answer_handler = widget_domain.AnswerHandler(
            input_type=objects.NonnegativeInt)
        self.assertEqual(len(answer_handler.rules), 1)


class WidgetUnitTests(test_utils.GenericTestBase):
    """Test the widget domain object and registry."""

    def test_parameterized_widget(self):
        """Test that parameterized widgets are correctly handled."""

        MUSIC_STAFF_ID = 'MusicStaff'

        widget = widget_domain.Registry.get_widget_by_id(
            feconf.INTERACTIVE_PREFIX, MUSIC_STAFF_ID)
        self.assertEqual(widget.id, MUSIC_STAFF_ID)
        self.assertEqual(widget.name, 'Music staff')

        code = widget.get_raw_code()
        self.assertIn('GLOBALS.noteToGuess = JSON.parse(\'\\"', code)

        code = widget.get_raw_code({'noteToGuess': 'abc'})
        self.assertIn('GLOBALS.noteToGuess = JSON.parse(\'\\"abc\\"\');', code)

        parameterized_widget_dict = widget.get_with_params(
            {'noteToGuess': 'abc'}
        )
        self.assertItemsEqual(parameterized_widget_dict.keys(), [
            'id', 'name', 'category', 'description',
            'params', 'handlers', 'raw'])
        self.assertEqual(parameterized_widget_dict['id'], MUSIC_STAFF_ID)
        self.assertIn('GLOBALS.noteToGuess = JSON.parse(\'\\"abc\\"\');',
                      parameterized_widget_dict['raw'])
        self.assertEqual(parameterized_widget_dict['params'], {
            'noteToGuess': {
                'value': 'abc',
                'obj_type': 'UnicodeString',
            }
        })


class WidgetUtilsUnitTests(unittest.TestCase):

    def test_convert_to_js_string(self):
        """Test convert_to_js_string method."""
        expected_values = [
            ('a', '\\"a\\"'),
            (2, '2'),
            (5.5, '5.5'),
            ("'", '\\"\\\'\\"'),
            (u'¡Hola!', '\\"\\\\u00a1Hola!\\"'),
            (['a', '¡Hola!', 2], '[\\"a\\", \\"\\\\u00a1Hola!\\", 2]'),
            ({'a': 4, '¡Hola!': 2}, '{\\"a\\": 4, \\"\\\\u00a1Hola!\\": 2}'),
            ('', '\\"\\"'),
            (None, 'null'),
            (['a', {'b': 'c', 'd': ['e', None]}],
                '[\\"a\\", {\\"b\\": \\"c\\", \\"d\\": [\\"e\\", null]}]')
        ]

        for tup in expected_values:
            self.assertEqual(widget_domain.convert_to_js_string(tup[0]), tup[1])
