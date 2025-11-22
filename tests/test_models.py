"""Tests for models.py - Database table schema definitions."""
import pytest
from models.source_models import (
    WISEInfoTable, TerminalControlTable, EmpNamesTable, DetailsTable,
    DLoadErrorsTable, ZoneTable, ZoneChangeQueueTable, ZoneChangeInfoTable,
    TagTable, TagRangeTable
)


class TestWISEInfoTable:
    """Test WISEInfoTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = WISEInfoTable()
        assert table.table == "tblWISEInfo"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = WISEInfoTable()
        assert table.job_datetime == "JobDateTime"
        assert table.name == "Name"
        assert table.address == "Address"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = WISEInfoTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"


class TestTerminalControlTable:
    """Test TerminalControlTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = TerminalControlTable()
        assert table.table == "tblTerminalControl"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = TerminalControlTable()
        assert table.emp_number == "TerminalUser"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = TerminalControlTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"


class TestEmpNamesTable:
    """Test EmpNamesTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = EmpNamesTable()
        assert table.table == "tblEmpNames"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = EmpNamesTable()
        assert table.emp_number == "EmpNo"
        assert table.emp_name == "Name"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = EmpNamesTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"


class TestDetailsTable:
    """Test DetailsTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = DetailsTable()
        assert table.table == "tblDetails"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = DetailsTable()
        assert table.emp_number == "empno"
        assert table.tag_number == "tag"
        assert table.upc == "sku"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = DetailsTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"


class TestDLoadErrorsTable:
    """Test DLoadErrorsTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = DLoadErrorsTable()
        assert table.table == "tblDLoadErrors"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = DLoadErrorsTable()
        assert table.error_msg == "ErrorMsg"
        assert table.emp_number == "empno"
        assert table.tag_number == "tag"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = DLoadErrorsTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"


class TestZoneTable:
    """Test ZoneTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = ZoneTable()
        assert table.table == "tblZone"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = ZoneTable()
        assert table.zone_id == "ZoneID"
        assert table.zone_description == "ZoneDesc"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = ZoneTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"


class TestZoneChangeQueueTable:
    """Test ZoneChangeQueueTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = ZoneChangeQueueTable()
        assert table.table == "tblZoneChangeQueue"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = ZoneChangeQueueTable()
        assert table.zone_queue_id == "ZoneQueueID"
        assert table.zone_id == "ZoneID"
        assert table.tag_number == "Tag"
        assert table.upc == "UPC"
        assert table.price == "Price"
        assert table.quantity == "Quantity"
        assert table.reason == "Reason"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = ZoneChangeQueueTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"


class TestZoneChangeInfoTable:
    """Test ZoneChangeInfoTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = ZoneChangeInfoTable()
        assert table.table == "tblZoneChangeInfo"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = ZoneChangeInfoTable()
        assert table.zone_queue_id == "ZoneQueueID"
        assert table.quantity == "CountedQty"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = ZoneChangeInfoTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"


class TestTagTable:
    """Test TagTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = TagTable()
        assert table.table == "tblTag"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = TagTable()
        assert table.tag_number == "TagNo"
        assert table.total_quantity == "TotalQty"
        assert table.total_price == "TotalEXTPRICE"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = TagTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"


class TestTagRangeTable:
    """Test TagRangeTable dataclass."""
    
    def test_table_name(self):
        """Test table name is correctly set."""
        table = TagRangeTable()
        assert table.table == "tblTagRange"
    
    def test_column_names(self):
        """Test column names are correctly set."""
        table = TagRangeTable()
        assert table.tag_val_from == "TagValFrom"
        assert table.tag_val_to == "TagValTo"
        assert table.total_quantity == "TotalQty"
        assert table.total_price == "TotalEXTPRICE"
        assert table.zone_id == "ZoneID"
    
    def test_immutable(self):
        """Test that the dataclass is frozen (immutable)."""
        table = TagRangeTable()
        with pytest.raises(AttributeError):
            table.table = "new_table"
