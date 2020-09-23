# -*- coding: utf-8 -*-
import arcpy
from iLader.helpers import PostgresHelper

def create_dummy(source):
    # Dummy-Eintrag in Source erstellen
    arcpy.AddField_management(source, "dummy", "TEXT", field_length = 10)
    dummy_rows = arcpy.InsertCursor(source)
    dummy_row = dummy_rows.newRow()
    dummy_row.setValue("dummy","dummy_text")
    dummy_rows.insertRow(dummy_row)
    del dummy_row
    del dummy_rows

def delete_dummy(self, source, table, host, db, db_user, port, pw):
    # Dummy Eintrag aus Quelle löschen
    arcpy.DeleteField_management(source,["dummy"])
    arcpy.DeleteRows_management(source)
    # Dummy Eintrag aus Ziel löschen
    sql_query = 'DELETE FROM ' + table
    PostgresHelper.db_sql(self, host, db, db_user, port, pw, sql_query)
