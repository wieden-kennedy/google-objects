# Google Objects
Thin, pythonic OO wrapper around Google's "google-api-python-client" library.
Currently supports Python 2.7 :snake::snake::snake:

## Installation
```bash
  $ pip install google-objects
```

## Usage
Requires a valid Google API Credentials object from Google's excellent oauth2lib library. For more information, visit [here](https://developers.google.com/identity/protocols/OAuth2).
 
### Google Drive

- [x] Retrieve drive 'About' information:

```python
  from google_objects import DriveAPI

  gdrive = DriveAPI(OAUTH2LIB_CREDS)
  about = gdrive.get_about()

  print about.email
  print about.name

  # prints link to profile photo
  print about.photo

  # ...
```

- [x] List files in drive by type:

```python
  files_by_type = {
      'slides': gdrive.list_files('presentation'),
      'folders': gdrive.list_files('folder'),
      'spreadsheets': gdrive.list_files('spreadsheets'),
  }

  for file in files_by_type['folders']:
    print file.id
    print file.name

  for file in files_by_type['spreadsheets']:
    # prints list of parent folder IDs
    print file.parents

  # ...
```

- [x] Copy and share file:

```python
	file = gdrive.get_file('FILE_ID')
	new_file = file.copy('NEW_FILE_NAME', ['PARENT_FOLDER_1', 'PARENT_FOLDER_2'])
	
	# allow myfriend@hotmail.com to view
	permission = new_file.add_permission('myfriend@hotmail.com')

	# print newly created permission information
	print permission.role, permission.type, permission.email
```

### Google Slides

- [x] Retrieve presentation and loop through elements:

```python
	from google_objects import SlidesAPI

	gslides = SlidesAPI(OAUTHLIB_CREDS)
	presentation = gslides.get_presentation('PRESENTATION_ID')

	# print slides attributes
	for slide in presentation:
		print slide.id

		for element in slide: # equivalent to 'for element in presentation.elements()' 	
			print element.type 
			# Shape, Table, etc
	
```

- [x] Check text in shape:

```python
	shape = presentation.get_element_by_id('SHAPE_ID')
	for segment in shape.text:
		print segment.text

```

- [x] Batch update every cell in table:

```python
	# use with to perform batch updates in block
	with presentation as pres:
		table = pres.get_element_by_id('TABLE_ID')
		for cell in table:
			print cell.location # tuple containing cell location
			for segment in cell.text:
				# update cell
				segment.text = 'UPDATED_VALUE'

```

### Google Sheets

- [x] Retrieve spreadsheet and loop through sheets:

```python
	from google_objects import SheetsAPI

	gsheets = SheetsAPI(OAUTHLIB_CREDS)
	spreadsheet = gsheets.get_spreadsheet('SPREADSHEET_ID')

	for sheet in spreadsheet:
		print sheet.id, sheet.title
```

- [x] Get sheet by ID and return its full block of values:

```python
	sheet = spreadsheet['SHEET_ID']
	values = sheet.values()	
```

- [x] Get named range value block:

```python
	named_ranges = spreadsheet.named_ranges('SHEET_NAME!A:C')
	for rng in named_range:
		values = named_range.get_block()
```

- [x] Loop through values block:

```python
	values = spreadsheet.get_range('SHEET_NAME!A:C')
	for row in values:
		for cell in row:
			print cell.value
```
