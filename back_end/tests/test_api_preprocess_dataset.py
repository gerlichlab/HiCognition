import sys
import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase, TempDirTestCase

# add path to import app
sys.path.append("./")
from app import db
from app.models import Dataset


class TestPreprocessDataset(LoginTestCase, TempDirTestCase):
    """Tests correct launching of
    pipelines after posting parameters to /preprocess route.
    Inherits both from LoginTest and TempDirTestCase
    to be able to login and make temporary directory"""

    def add_test_datasets(self):
        """adds test datasets to db"""
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            user_id=1
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="fdsa4321",
            filetype="cooler",
            user_id=1
        )
        dataset3 = Dataset(
            dataset_name="test3",
            file_path="/test/path/3",
            higlass_uuid="fdsa8765",
            filetype="bedfile",
            user_id=2
        )
        db.session.add(dataset1)
        db.session.add(dataset2)
        db.session.add(dataset3)
        db.session.commit()

    @patch("app.models.User.launch_task")
    def test_pipeline_pileup_is_called_correctly(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add datasets
        self.add_test_datasets()
        data = {
            "dataset_id": "1",
            "interval_ids": "[1, 2, 3, 4]",
            "binsizes": "[10000, 20000, 40000]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        mock_launch.assert_called_with(
            "pipeline_pileup",
            "run pileup pipeline",
            1,
            [10000, 20000, 40000],
            [1, 2, 3, 4],
        )

    @patch("app.models.User.launch_task")
    def test_user_cannot_access_other_datasets(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add datasets
        self.add_test_datasets()
        data = {
            "dataset_id": "3",
            "interval_ids": "[1, 2, 3, 4]",
            "binsizes": "[10000, 20000, 40000]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    @patch("app.models.User.launch_task")
    def test_404_on_non_existent_dataset(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add datasets
        self.add_test_datasets()
        data = {
            "dataset_id": "4",
            "interval_ids": "[1, 2, 3, 4]",
            "binsizes": "[10000, 20000, 40000]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 404)

    @patch("app.models.User.launch_task")
    def test_400_on_bad_form(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add datasets
        self.add_test_datasets()
        data = {
            "interval_ids": "[1, 2, 3, 4]",
            "binsizes": "[10000, 20000, 40000]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.models.User.launch_task")
    def test_pipeline_pileup_is_called_correctly_for_public_unowned_dataset(self, mock_launch):
        """Tests whether cooler pipeline to do pileups is called correctly."""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        token_headers = self.get_token_header(token)
        # add datasets
        dataset1 = Dataset(
            dataset_name="test1",
            file_path="/test/path/1",
            higlass_uuid="asdf1234",
            filetype="cooler",
            public=True,
            user_id=2
        )
        dataset2 = Dataset(
            dataset_name="test2",
            file_path="/test/path/2",
            higlass_uuid="fdsa4321",
            filetype="cooler",
            public=True,
            user_id=2
        )
        dataset3 = Dataset(
            dataset_name="test3",
            file_path="/test/path/3",
            higlass_uuid="fdsa8765",
            filetype="bedfile",
            user_id=2
        )
        db.session.add(dataset1)
        db.session.add(dataset2)
        db.session.add(dataset3)
        db.session.commit()
        data = {
            "dataset_id": "1",
            "interval_ids": "[1, 2, 3, 4]",
            "binsizes": "[10000, 20000, 40000]",
        }
        # dispatch post request
        response = self.client.post(
            "/api/preprocess/",
            data=data,
            headers=token_headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        # check whether pipeline has been called with right parameters
        mock_launch.assert_called_with(
            "pipeline_pileup",
            "run pileup pipeline",
            1,
            [10000, 20000, 40000],
            [1, 2, 3, 4],
        )


if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
