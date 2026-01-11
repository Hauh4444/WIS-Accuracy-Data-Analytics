import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from utils.report_generator import generate_accuracy_report


@pytest.fixture
def q_app():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


def setup_basic_mocks(mock_env, mock_pdf, template_names):
    env_instance = MagicMock()
    mock_env.return_value = env_instance

    templates = []
    for name in template_names:
        tmpl = MagicMock()
        tmpl.render.return_value = f"<html>{name}</html>"
        templates.append(tmpl)

    env_instance.get_template.side_effect = templates
    mock_pdf.return_value = MagicMock(err=False)
    return templates


def test_generate_report_standard_success(q_app):
    store_data = {"store": "ABC"}
    emp_data = [{"uph": 5, "total_quantity": 10}]
    zone_data = [{"zone_id": 2}]

    with patch("utils.report_generator.webbrowser.open") as mock_web, \
         patch("utils.report_generator.pisa.CreatePDF") as mock_pdf, \
         patch("utils.report_generator.Environment") as mock_env, \
         patch("utils.report_generator.Path.exists", return_value=True) as mock_exists, \
         patch("utils.report_generator.resource_path", side_effect=lambda p: f"/fake/{p}") as mock_res:

        setup_basic_mocks(mock_env, mock_pdf, ["emp_report.html", "zone_report.html", "disc_report.html"])
        generate_accuracy_report(store_data, emp_data, zone_data, season=False)

        assert mock_env.called
        assert mock_pdf.called
        assert mock_web.called


def test_generate_report_season_success(q_app):
    store_data = {"store": "ABC"}
    emp_data = [{"uph": 5, "total_quantity": 10}]
    zone_data = [{"zone_id": 2}]

    with patch("utils.report_generator.webbrowser.open") as mock_web, \
         patch("utils.report_generator.pisa.CreatePDF") as mock_pdf, \
         patch("utils.report_generator.Environment") as mock_env, \
         patch("utils.report_generator.Path.exists", return_value=True) as mock_exists, \
         patch("utils.report_generator.resource_path", side_effect=lambda p: f"/fake/{p}") as mock_res:

        setup_basic_mocks(mock_env, mock_pdf, ["date_range_emp_report.html", "date_range_zone_report.html"])
        generate_accuracy_report(store_data, emp_data, zone_data, season=True)

        assert mock_env.called
        assert mock_pdf.called
        assert mock_web.called


def test_generate_report_empty_store_data(q_app):
    with patch("utils.report_generator.QtWidgets.QMessageBox.warning") as mock_msg:
        with pytest.raises(ValueError):
            generate_accuracy_report({}, [{"uph": 1, "total_quantity": 2}], [{"zone_id": 1}])
        assert mock_msg.called


def test_generate_report_invalid_lists(q_app):
    with patch("utils.report_generator.QtWidgets.QMessageBox.warning") as mock_msg:
        with pytest.raises(ValueError):
            generate_accuracy_report({"store": "ABC"}, "not-list", [])
        assert mock_msg.called


def test_missing_templates_dir(q_app):
    with patch("utils.report_generator.Path.exists", return_value=False) as mock_exists, \
         patch("utils.report_generator.QtWidgets.QMessageBox.warning") as mock_msg:
        with pytest.raises(RuntimeError):
            generate_accuracy_report({"store": "ABC"}, [], [])
        assert mock_msg.called


def test_missing_specific_template(q_app):
    with patch("utils.report_generator.resource_path", side_effect=lambda p: f"/fake/{p}") as mock_res, \
         patch("utils.report_generator.Path.exists", side_effect=[True, False]) as mock_exists, \
         patch("utils.report_generator.QtWidgets.QMessageBox.warning") as mock_msg:
        with pytest.raises(RuntimeError):
            generate_accuracy_report({"store": "ABC"}, [], [], season=False)
        assert mock_msg.called


def test_pdf_generation_error(q_app):
    store_data = {"store": "ABC"}
    emp_data = [{"uph": 5, "total_quantity": 10}]
    zone_data = [{"zone_id": 2}]

    with patch("utils.report_generator.webbrowser.open") as mock_web, \
         patch("utils.report_generator.pisa.CreatePDF") as mock_pdf, \
         patch("utils.report_generator.Environment") as mock_env, \
         patch("utils.report_generator.Path.exists", return_value=True) as mock_exists, \
         patch("utils.report_generator.resource_path", side_effect=lambda p: f"/fake/{p}") as mock_res, \
         patch("utils.report_generator.QtWidgets.QMessageBox.warning") as mock_msg:

        setup_basic_mocks(mock_env, mock_pdf, ["emp_report.html", "zone_report.html", "disc_report.html"])
        mock_pdf.return_value.err = True 

        with pytest.raises(RuntimeError):
            generate_accuracy_report(store_data, emp_data, zone_data)

        assert mock_msg.called
        mock_web.assert_not_called()


def test_unexpected_exception_handling(q_app):
    with patch("utils.report_generator.Path.exists", return_value=True) as mock_exists, \
         patch("utils.report_generator.resource_path", side_effect=lambda p: f"/fake/{p}") as mock_res, \
         patch("utils.report_generator.Environment", side_effect=Exception("Env fail")) as mock_env, \
         patch("utils.report_generator.QtWidgets.QMessageBox.warning") as mock_msg:

        with pytest.raises(Exception):
            generate_accuracy_report({"store": "ABC"}, [], [])
        assert mock_msg.called
