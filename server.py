# Created by Anmol Bhargava

import os
import swiftclient
import keystoneclient
import pyDes
from flask import Flask, request, render_template

app = Flask(__name__)

# Key for encrypting file content
k = pyDes.des(b"MYNEWKEY", pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

# Establish connection to IBM ObjectStorage
auth_url = "https://identity.open.softlayer.com/v3"
password = "" # insert your Object Storage instance password here
project_id = "" # insert your Object Storage instance project id here
user_id = "" # insert your Object Storage instance user id here
region_name = ""
conn = 	swiftclient.Connection (key=password, 
                                authurl=auth_url,
                                auth_version='3',
                                os_options={"project_id" : project_id,
                                            "user_id" : user_id, 
                                            "region_name" : region_name})

conn.put_container("test_container") # Create new container in Object Storage

@app.route('/')
def Welcome():
    return render_template('index.html')

@app.route('/upload',methods=['GET','POST'])
def Upload():
  if request.method=='POST':
    file= request.files['file_upload']
    filename=file.filename
    content=file.read()
    encryptedD = k.encrypt(content)
    conn.put_object("test_container", 
		filename, 
		contents = encryptedD, 
		content_type="text")
    
    return '<h1>Awesome! Files uploaded.<h1><br><form action="../"><input type="Submit" value="Lets go back"></form>'

@app.route('/download',methods=['GET','POST'])
def Download():
    if request.method=='POST':
      filename = request.form['file_download']
      file = conn.get_object("test_container",filename)
      fileContentsBytes = file[1]#str(file)
      fileContents = k.decrypt(fileContentsBytes).decode('UTF-8')
    return '<h3>The File is,</h3><br><br>' + fileContents + '<br><br><form action="../"><input type="Submit" value="Lets go back"></form>'

@app.route('/delete',methods=['GET','POST'])
def Delete():
    if request.method=='POST':
      filename = request.form['file_delete']
      conn.delete_object("test_container",filename)

    return '<h3>The File has been successfully deleted,</h3><br><br><form action="../"><input type="Submit" value="Lets go back"></form>'

@app.route('/list')
def List():
  listOfFiles = ""
  for container in conn.get_account()[1]:
    for data in conn.get_container(container['name'])[1]:
      if not data:
        listOfFiles = listOfFiles + "<i> No files are currently present on Cloud.</i>"
      else:
        listOfFiles = listOfFiles + "<li>" + 'File: {0}\t Size: {1}\t Date: {2}'.format(data['name'], data['bytes'], data['last_modified']) + "</li><br>"
  return '<h3>The files currently on cloud are </h3><br><br><ol>' + listOfFiles + '<br><form action="../"><input type="Submit" value="Lets go back"></form>'

# Port set as 8000 as per IBM Bluemix Environment
port = os.getenv('PORT', '8000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
