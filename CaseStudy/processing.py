#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if the second level tag "k" value contains problematic characters, it should be ignored
- if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if the second level tag "k" value does not start with "addr:", but contains ":", you can
  process it in a way that you feel is best. For example, you might split it into a two-level
  dictionary like with "addr:", or otherwise convert the ":" to create a valid key.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def get_pos(element):
    # to return the latituede and longitude of a place in array
    lat = float(element.attrib['lat'])
    lon = float(element.attrib['lon'])
    pos = [lat, lon]
    return pos

def fix_postcode(v):
    """
    Reduces postcodes to 5 digit strings. Some zips take the form
    'NC12345' or '12345-6789' hindering MongoDB aggregations.
    """
    postcode = ''
    for char in v:
        if char.isdigit():
            postcode += char
        if len(postcode) == 5:
            break
    return postcode
                    

def node_update_k(node, value, tag):
    """Adds 'k' and 'v' values from tag as new key:value pair to node."""
    k = value
    v = tag.attrib['v']                       
    if k.startswith('addr:'):
        # Ignore 'addr:street:' keys with 2 colons
        if k.count(':') == 1:
            if 'address' not in node:
                node['address'] = {}
            if k == 'addr:postcode' and len(v) > 5:
                v = fix_postcode(v)
            # Fix all substrings of street names using a
            # more generalized update method from audit.py
            elif k == 'addr:street':
                v = audit.update(v, audit.mapping)
            node['address'][k[5:]] = v
    # Check for highway exit number nodes
    elif k == 'ref' and node['type'] == 'node':
        node['exit_number'] = v
    # Check for 'k' values that equal the string 'type'
    # which would overwrite previously written node['type']
    elif k == 'type':
        node['service_type'] = v
    # Process other k:v pairs normally
    else:
        node[k] = v
return node




def join_segments(s):
    """
    Joins 'tiger:__' street name substring values (prefix, base,
    type, suffix) in dict s to a string
    """
    for segment in s:
        if segment in audit.mapping:
            s[segment] = audit.mapping[segment]
    ordered = [ s['name_direction_prefix'], s['name_base'],
                s['name_type'], s['name_direction_suffix'],
                s['name_direction_suffix_1'] ]
    segments = [s for s in ordered if s]
return ' '.join(segments)

def ignoring(k):
     KEYS = ['ele', 'import_uuid', 'source', 'wikipedia']
     PREFIXES = ['gnis:', 'is_in', 'nhd-s']
     
     if k in KEYS or k[:5] in PREFIXES:
         return True
     return False

def process_tag(node, value, tag):
     """
    Adds a Tiger GPS value ('tiger:__') from the tag as a new
    key:value pair to node['address']
    """
    name_segments = ['name_type', 'name_base', 'name_direction_prefix', 
    'name_direction_suffix', 'name_direction_suffix_1']
    k = value[6:]
    v = tag.attrib['v']
    
    if 'address' not in node:
        node['address'] = {}
        
    if 'name' in node:
          node['address']['street'] = node['name']
    elif k == 'zip_left':
        node['address']['postcode'] = v
    elif k in name_segments:
        if 'street' not in node['address']:
            node['address']['street'] = {k:'' for k in name_segments}
        elif isinstance(node['address']['street'], dict):
            node['address']['street'][k] = v
    return node



def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node['type'] = element.tag
        node['created'] = {}
        
        if 'lat' in element.attrib:
            node['pos'] = get_pos(element)
        
        
        #begin iterating over subtags
        for tag in element.iter():
            for key, value in tag.items():
                
                if key in CREATED:
                    node['created'][key] = value
                    
                #check for problem characters and ignored values in second level tag
                elif key == 'k' and not re.search(problemchars, value):
                    if not ignoring(value):
                        if value.startswith('tiger:'):
                            node = process_tiger(node, value, tag)
                        else:
                            node = node_update_k(node, value, tag)
                            
                # Create/update array 'node_refs'
                elif key == 'ref':
                    if 'node_refs' not in node:
                        node['node_refs'] = []
                    node['node_refs'].append(value)
                # Process remaining tags
                elif key not in ['v', 'lat', 'lon']:
                    node[key] = value
        if 'address' in node and 'street' in node['address']:
            if isinstance(node['address']['street'], dict):
                # Replace saved dict of street name segments with full street name
                node['address']['street'] = join_segments(node['address']['street'])
        # Safe to clear() now that element has been processed
        element.clear()
return node
        
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('example.osm', True)
    #pprint.pprint(data)
    
    correct_first_elem = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()
