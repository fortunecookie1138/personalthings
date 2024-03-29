#!/usr/bin/python

###############################
# 
# For Brian! For Lyndsey! For monies!!!
# We are automating the following manual steps:
# Login to Wuufoo -> Forms -> (ideally filter to "done", but I can't do that via API) For each result, click "All Entries" -> select all entries via checkbox -> click "download entries" (as CSV)
#
##############################

import requests
import json

class form:
  name = ""
  hash = ""
  url = ""

formHashToTest = ""
baseUrl = "https://bbwebforms.wufoo.com/api/v3"
apiKey = "OUN1-GRDN-7IXP-7ESW"
printResponses = False

def callWufooApi(fullUrl):
  print("Calling endpoint: " + fullUrl)
    
  response = requests.get(fullUrl, auth=(apiKey, "doesnotmatter"))
  if response.status_code != 200:
    print("Uh oh! Got back an HTTP "+str(response.status_code)+" reponse when calling '"+fullUrl+"'")

  if printResponses:
      print("Response from '"+fullUrl+"'")
      print(response.text)

  return json.loads(response.text)

def retrieveForms(baseUrl):
  parsed = callWufooApi(baseUrl+"/forms.json")

  forms = []
  for x in parsed["Forms"]:
    parsedForm = form()
    parsedForm.name = x["Name"]
    parsedForm.hash = x["Hash"]
    parsedForm.url = x["Url"]
    forms.append(parsedForm)

  return forms

def retrieveFormFields(baseUrl, formHash):
  parsed = callWufooApi(baseUrl+"/forms/"+formHash+"/fields.json?system=true")

  fieldsDictionary = {}
  for field in parsed["Fields"]:
    fieldID = field["ID"]
    fieldLabel = field["Title"]
    if "SubFields" in field:
      print("There are subfields under "+fieldLabel)
      for subfield in field["SubFields"]:
        subfieldID = subfield["ID"]
        subfieldLabel = subfield["Label"]
        fieldsDictionary[subfieldID] = fieldLabel + " (" + subfieldLabel + ")"
    else:
      fieldsDictionary[fieldID] = fieldLabel

  return fieldsDictionary

def retrieveEntries(baseUrl, formHash):
  allEntries = []
  gotEntries = True
  entryStartIndex = 0
  pageSize = 100
  while gotEntries == True:
    parsed = callWufooApi(baseUrl+"/forms/"+formHash+"/entries.json?system=true&pageStart="+str(entryStartIndex)+"&pageSize="+str(pageSize))
    entries = parsed["Entries"]
    print(entries)
    if (len(entries) == 0):
      gotEntries = False
    else:
      allEntries = allEntries + entries
      entryStartIndex += pageSize

  return allEntries

def escapeQuotes(value):
  replaced = value.replace("\"", "\"\"")
  return replaced

def matchEntryFields(fields, entries):
  outputLines = []
  
  headerLine = "\"" + '","'.join(escapeQuotes(str(x)) for x in fields.values()) + "\""
  outputLines.append(headerLine.replace("\r\n", "  ") + "\n")

  for entry in sorted(entries, key=lambda x : int(x["EntryId"]), reverse=True):
    entryLine = "\"" + '","'.join(escapeQuotes(str(x)) for x in entry.values()) + "\""
    outputLines.append(entryLine.replace("\r\n", "  ") + "\n")

  return outputLines

def writeCSV(baseOutputPath, form, lines):
  print("Writing lines for form hash "+form.hash)
  print(lines)
  outputFilename = form.url+".csv"

  f = open(baseOutputPath + "\\" + outputFilename, "wb")
  for line in lines:
    f.write(line.encode())
  f.close()

forms = retrieveForms(baseUrl)
print("There are "+str(len(forms))+" forms to work through")

for form in [x for x in forms if formHashToTest == "" or x.hash == formHashToTest]:
  print("Looking at form with hash "+form.hash+" named '"+form.name+"'")
  fields = retrieveFormFields(baseUrl, form.hash)
  entries = retrieveEntries(baseUrl, form.hash)
  print("This form has "+str(len(entries))+" entries")
  linesToWrite = matchEntryFields(fields, entries)
  writeCSV("C:\src\personalthings\Lyndsey\WufooFormEntryDownloader\Output", form, linesToWrite)
