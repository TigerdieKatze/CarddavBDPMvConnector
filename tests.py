import unittest
from unittest.mock import patch, MagicMock
from models import UserDto
from carddav_sync import (
    apply_group_mapping,
    add_default_group,
    update_group_membership,
    find_or_create_vcard
)
from mv_integration import convert_excel_to_userdto
from notifications import send_email
import vobject

class TestCarddavBDPMvConnector(unittest.TestCase):

    def setUp(self):
        self.test_config = {
            "GROUP_MAPPING": {"Group1": "MappedGroup1", "Group2": "MappedGroup2"},
            "DEFAULT_GROUP": "DefaultGroup",
            "APPLY_GROUP_MAPPING_TO_PARENTS": False,
            "APPLY_DEFAULT_GROUP_TO_PARENTS": True
        }

    def test_apply_group_mapping(self):
        groups = ["Group1", "Group3"]
        mapped_groups = apply_group_mapping(groups, False)
        self.assertIn("MappedGroup1", mapped_groups)
        self.assertIn("Group3", mapped_groups)
        self.assertNotIn("Group2", mapped_groups)

    def test_add_default_group(self):
        groups = ["Group1"]
        final_groups = add_default_group(groups, False)
        self.assertIn("DefaultGroup", final_groups)
        self.assertIn("Group1", final_groups)

    def test_update_group_membership(self):
        vcard = vobject.vCard()
        groups = ["Group1", "Group2"]
        update_group_membership(vcard, groups, False)
        self.assertIn("categories", vcard.contents)
        self.assertEqual(set(vcard.categories.value), set(["MappedGroup1", "MappedGroup2", "DefaultGroup"]))

    def test_update_group_membership_parent(self):
        vcard = vobject.vCard()
        groups = ["Group1", "Group2"]
        update_group_membership(vcard, groups, True)
        self.assertIn("categories", vcard.contents)
        self.assertEqual(set(vcard.categories.value), set(["DefaultGroup", "Eltern"]))

    def test_find_or_create_vcard_existing(self):
        contacts = [
            ("href1", "etag1", "BEGIN:VCARD\nFN:John Doe\nEND:VCARD"),
            ("href2", "etag2", "BEGIN:VCARD\nFN:Jane Doe\nEND:VCARD")
        ]
        vcard, href, etag = find_or_create_vcard(contacts, "John Doe")
        self.assertEqual(vcard.fn.value, "John Doe")
        self.assertEqual(href, "href1")
        self.assertEqual(etag, "etag1")

    def test_find_or_create_vcard_new(self):
        contacts = [
            ("href1", "etag1", "BEGIN:VCARD\nFN:Jane Doe\nEND:VCARD")
        ]
        vcard, href, etag = find_or_create_vcard(contacts, "John Doe")
        self.assertIsInstance(vcard, vobject.vCard)
        self.assertIsNone(href)
        self.assertIsNone(etag)

    @patch('pandas.read_excel')
    def test_convert_excel_to_userdto(self, mock_read_excel):
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {'Status': 'Aktiv', 'Vorname': 'John', 'Nachname': 'Doe', 'eMail': 'john@example.com', 'eMail2': None, 'eMail_Eltern': None, 'Kleingruppe': 'Group1'}),
            (1, {'Status': 'Inaktiv', 'Vorname': 'Jane', 'Nachname': 'Doe', 'eMail': 'jane@example.com', 'eMail2': None, 'eMail_Eltern': None, 'Kleingruppe': 'Group2'}),
        ]
        mock_read_excel.return_value = mock_df

        users = convert_excel_to_userdto('dummy_path')
        self.assertEqual(len(users), 1)
        self.assertIsInstance(users[0], UserDto)
        self.assertEqual(users[0].firstname, 'John')
        self.assertEqual(users[0].lastname, 'Doe')
        self.assertEqual(users[0].own_email, 'john@example.com')
        self.assertEqual(users[0].groups, ['Group1'])

    @patch('smtplib.SMTP')
    @patch('config.CONFIG', {'SMTP_USERNAME': 'test', 'NOTIFICATION_EMAIL': 'admin@example.com', 'SMTP_SERVER': 'smtp.example.com', 'SMTP_PORT': 587})
    def test_send_email(self, mock_smtp):
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        send_email('Test Subject', 'Test Body')

        mock_smtp_instance.send_message.assert_called_once()
        args, kwargs = mock_smtp_instance.send_message.call_args
        self.assertEqual(args[0]['Subject'], 'Test Subject')
        self.assertEqual(args[0]['From'], 'test')
        self.assertEqual(args[0]['To'], 'admin@example.com')

if __name__ == '__main__':
    unittest.main()