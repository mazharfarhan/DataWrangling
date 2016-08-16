# -*- coding: utf-8 -*-
'''
Find the time and value of max load for each of the regions
COAST, EAST, FAR_WEST, NORTH, NORTH_C, SOUTHERN, SOUTH_C, WEST
and write the result out in a csv file, using pipe character | as the delimiter.

An example output can be seen in the "example.csv" file.
'''

import xlrd
import os
import csv
from zipfile import ZipFile

datafile = "2013_ERCOT_Hourly_Load_Data.xls"
outfile = "2013_Max_Loads.csv"


def open_zip(datafile):
    with ZipFile('{0}.zip'.format(datafile), 'r') as myzip:
        myzip.extractall()


def parse_file(datafile):
    workbook = xlrd.open_workbook(datafile)
    sheet = workbook.sheet_by_index(0)
    data = [[ sheet.cell_value(r, col) for col in range(sheet.ncols)] for r in range(sheet.nrows)]
    coast = sheet.col_values(1, start_rowx=1, end_rowx=None)
    east  = sheet.col_values(2, start_rowx=1, end_rowx=None)
    far_west = sheet.col_values(3, start_rowx=1, end_rowx=None)
    north  = sheet.col_values(4, start_rowx=1, end_rowx=None)
    north_c = sheet.col_values(5, start_rowx=1, end_rowx=None)
    southern  = sheet.col_values(6, start_rowx=1, end_rowx=None)
    south_c = sheet.col_values(7, start_rowx=1, end_rowx=None)
    west  = sheet.col_values(8, start_rowx=1, end_rowx=None)
    
    
    maxcoast = max(coast)
    maxeast = max(east)
    maxfar_west= max(far_west)
    maxnorth = max(north)
    maxnorth_c = max(north_c)
    maxsouthern = max(southern)
    maxsouth_c = max(south_c)
    maxwest = max(west)
    
    
    coastpos = coast.index(maxcoast) + 1
    eastpos =  east.index(maxeast) + 1
    farwestpos = far_west.index(maxfar_west) + 1
    northpos = north.index(maxnorth) + 1
    northcpos = north_c.index(maxnorth_c) + 1
    southernpos = southern.index(maxsouthern) + 1
    southcpos = south_c.index(maxsouth_c) + 1
    westpos = west.index(maxwest) + 1
    
    
    coasttime = sheet.cell_value(coastpos,0)
    realcoasttime = xlrd.xldate_as_tuple(coasttime,0)
    easttime = sheet.cell_value(eastpos,0)
    realeasttime = xlrd.xldate_as_tuple(easttime,0)
    farwesttime = sheet.cell_value(farwestpos,0)
    realfarwesttime = xlrd.xldate_as_tuple(farwesttime,0)
    northtime = sheet.cell_value(northpos,0)
    realnorthtime = xlrd.xldate_as_tuple(northtime,0)
    northctime = sheet.cell_value(northcpos,0)
    realnorthctime = xlrd.xldate_as_tuple(northctime,0)
    southerntime = sheet.cell_value(southernpos,0)
    realsoutherntime = xlrd.xldate_as_tuple(southerntime,0)
    southctime = sheet.cell_value(southcpos,0)
    realsouthctime = xlrd.xldate_as_tuple(southctime,0)
    westtime = sheet.cell_value(westpos,0)
    realwesttime = xlrd.xldate_as_tuple(westtime,0)
    
    print realcoasttime[0];
    quit()
    
    
    data = {
     
        "maxcoast" : maxcoast,
        "maxeast": maxeast,
        "maxfar_west" : maxfar_west,
        "maxnorth": maxnorth,
        "maxnorth_c" : maxnorth_c,
        "maxsouthern": maxsouthern,
        "maxsouth_c" : maxsouth_c,
        "maxwest": maxwest,
        "coasttime":realcoasttime,
        "easttime":realeasttime,
        "farwesttime":realfarwesttime,
        "northtime":realnorthtime,
        "northctime":realnorthctime,
        "southerntime":realsoutherntime,
        "southctime":realsouthctime,
        "westtime":realwesttime
    
    }    
    
    # YOUR CODE HERE
    # Remember that you can use xlrd.xldate_as_tuple(sometime, 0) to convert
    # Excel date to Python tuple of (year, month, day, hour, minute, second)
    return data

def save_file(data, filename):
    # YOUR CODE HERE
    
    with open(filename, "wb") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter = "|")
        csvwriter.writerow(["Station","Year","Month","Day","Hour","Max Load"])
        csvwriter.writerow(["COAST",data["coasttime"][0]])
    
    
def test():
    open_zip(datafile)
    data = parse_file(datafile)
    save_file(data, outfile)

    number_of_rows = 0
    stations = []

    ans = {'FAR_WEST': {'Max Load': '2281.2722140000024',
                        'Year': '2013',
                        'Month': '6',
                        'Day': '26',
                        'Hour': '17'}}
    correct_stations = ['COAST', 'EAST', 'FAR_WEST', 'NORTH',
                        'NORTH_C', 'SOUTHERN', 'SOUTH_C', 'WEST']
    fields = ['Year', 'Month', 'Day', 'Hour', 'Max Load']

    with open(outfile) as of:
        csvfile = csv.DictReader(of, delimiter="|")
        for line in csvfile:
            station = line['Station']
            if station == 'FAR_WEST':
                for field in fields:
                    # Check if 'Max Load' is within .1 of answer
                    if field == 'Max Load':
                        max_answer = round(float(ans[station][field]), 1)
                        max_line = round(float(line[field]), 1)
                        assert max_answer == max_line

                    # Otherwise check for equality
                    else:
                        assert ans[station][field] == line[field]

            number_of_rows += 1
            stations.append(station)

        # Output should be 8 lines not including header
        assert number_of_rows == 8

        # Check Station Names
        assert set(stations) == set(correct_stations)

        
if __name__ == "__main__":
    test()
