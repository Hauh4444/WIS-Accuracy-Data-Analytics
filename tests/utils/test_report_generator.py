import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from utils import generate_accuracy_report


@pytest.fixture
def qt_app(qtbot):
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


def setup_basic_mocks(mock_env, mock_template, mock_pdf, template_names):
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


@patch("report_generator.webbrowser.open")
@patch("report_generator.pisa.CreatePDF")
@patch("report_generator.Environment")
@patch("report_generator.Path.exists", return_value=True)
@patch("report_generator.resource_path", side_effect=lambda p: f"/fake/{p}")
def test_generate_report_standard_success(mock_res, mock_exists, mock_env, mock_pdf, mock_web, qt_app):
    store_data = {"store": "ABC"}
    emp_data = [{"uph": 5, "total_quantity": 10}]
    zone_data = [{"zone_id": 2}]

    setup_basic_mocks(mock_env, MagicMock(), mock_pdf,
                      ["emp_report.html", "zone_report.html", "disc_report.html"])

    generate_accuracy_report(store_data, emp_data, zone_data, season=False)

    assert mock_env.called
    assert mock_pdf.called
    assert mock_web.called


@patch("report_generator.webbrowser.open")
@patch("report_generator.pisa.CreatePDF")
@patch("report_generator.Environment")
@patch("report_generator.Path.exists", return_value=True)
@patch("report_generator.resource_path", side_effect=lambda p: f"/fake/{p}")
def test_generate_report_season_success(mock_res, mock_exists, mock_env, mock_pdf, mock_web, qt_app):
    store_data = {"store": "ABC"}
    emp_data = [{"uph": 5, "total_quantity": 10}]
    zone_data = [{"zone_id": 2}]

    setup_basic_mocks(mock_env, MagicMock(), mock_pdf,
                      ["season_emp_report.html", "season_zone_report.html"])

    generate_accuracy_report(store_data, emp_data, zone_data, season=True)

    assert mock_env.called
    assert mock_pdf.called
    assert mock_web.called


@patch("report_generator.QtWidgets.QMessageBox.warning")
def test_generate_report_empty_store_data(mock_msg, qt_app):
    with pytest.raises(ValueError):
        generate_accuracy_report({}, [{"uph": 1, "total_quantity": 2}], [{"zone_id": 1}])

    assert mock_msg.called


@patch("report_generator.QtWidgets.QMessageBox.warning")
def test_generate_report_invalid_lists(mock_msg, qt_app):
    with pytest.raises(ValueError):
        generate_accuracy_report({"store": "ABC"}, "not-list", [])

    assert mock_msg.called


@patch("report_generator.Path.exists", return_value=False)
@patch("report_generator.QtWidgets.QMessageBox.warning")
def test_missing_templates_dir(mock_msg, mock_exists, qt_app):
    with pytest.raises(RuntimeError):
        generate_accuracy_report({"store": "ABC"}, [], [])

    assert mock_msg.called


@patch("report_generator.resource_path", side_effect=lambda p: f"/fake/{p}")
@patch("report_generator.Path.exists", side_effect=[True, False])
@patch("report_generator.QtWidgets.QMessageBox.warning")
def test_missing_specific_template(mock_msg, mock_exists, mock_res, qt_app):
    with pytest.raises(RuntimeError):
        generate_accuracy_report({"store": "ABC"}, [], [], season=False)

    assert mock_msg.called


@patch("report_generator.webbrowser.open")
@patch("report_generator.pisa.CreatePDF")
@patch("report_generator.Environment")
@patch("report_generator.Path.exists", return_value=True)
@patch("report_generator.resource_path", side_effect=lambda p: f"/fake/{p}")
@patch("report_generator.QtWidgets.QMessageBox.warning")
def test_pdf_generation_error(mock_msg, mock_res, mock_exists, mock_env, mock_pdf, mock_web, qt_app):
    store_data = {"store": "ABC"}
    emp_data = [{"uph": 5, "total_quantity": 10}]
    zone_data = [{"zone_id": 2}]

    setup_basic_mocks(mock_env, MagicMock(), mock_pdf,
                      ["emp_report.html", "zone_report.html", "disc_report.html"])
    mock_pdf.return_value = MagicMock(err=True)

    with pytest.raises(RuntimeError):
        generate_accuracy_report(store_data, emp_data, zone_data)

    assert mock_msg.called
    mock_web.assert_not_called()


@patch("report_generator.Path.exists", return_value=True)
@patch("report_generator.resource_path", side_effect=lambda p: f"/fake/{p}")
@patch("report_generator.Environment", side_effect=Exception("Env fail"))
@patch("report_generator.QtWidgets.QMessageBox.warning")
def test_unexpected_exception_handling(mock_msg, mock_env, mock_res, mock_exists, qt_app):
    with pytest.raises(Exception):
        generate_accuracy_report({"store": "ABC"}, [], [])

    assert mock_msg.called
