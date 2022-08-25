import importlib
import locale
import logging
import os
import socketserver
import sys
import time
from http import server
import re
import json

config={}


def delSingleFile(file_path):
	if os.path.isfile(file_path):
		os.remove(file_path)
		print("Deleting file:"+file_path)
	else:
		print("File "+file_path+" not found")


def toggleTag2Foto(foto,tag):
	#load
	try:
		f= open('data.json')
		data = json.load(f)
	except:
		data={}
	
	#change
	if not foto in  data:
		data[foto]=[]
	
	#toggle tag from foto (add or remove if exist)
	if tag not in data[foto]: 
		data[foto].append(tag)
	else:
		data[foto].remove(tag)
	
	#write
	json_data = json.dumps(data, sort_keys=True,indent=4)
	f = open('data.json', 'w')
	f.write(json_data)



def delFile(fileDir,fileName):
	file_path=fileDir+fileName
	toggleTag2Foto(file_path,"delete")
	#delSingleFile(fileDir+fileName)
	#delSingleFile(fileDir+"thumbnails/"+fileName)
	#delSingleFile(config["runDir"]+config["source"]+"/"+fileDir+fileName)
	#regenerataSig()


def regenerataSig():
	olddir = os.getcwd()
	os.chdir(config["runDir"])
	os.system('sigal build')
	os.chdir(olddir)

def getTags(fileName):
	try:
		f= open('data.json')
		data = json.load(f)
	except:
		data={}
	
	if not fileName in  data:
		data[fileName]=[]
	
	return json.dumps(data[fileName])


class PouServerHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        #print("POU:")
        #print(self.headers)
        #print(self.path)
        if "deleteFile=" in self.path:
           fileDir=self.path
           fileDir=re.sub(r'.*deleteDir=([^&]*).*', r'\1', fileDir)
           
           fileName=self.path
           fileName=re.sub(r'.*deleteFile=([^&]*).*', r'\1', fileName)
           
           print("Found! -> deleting: "+fileDir+fileName)
           delFile(fileDir,fileName)
           self.send_response(200)
           self.send_header('Content-type', 'text/html')
           self.end_headers()
           #delFile()
        elif "getTags" in self.path:
           fileName=self.path
           fileName=re.sub(r'.*fileName=([^&]*).*', r'\1', fileName)
           self.send_response(200)
           self.send_header('Content-type', 'text/html')
           self.end_headers()
           self.wfile.write(bytes(getTags(fileName), "utf-8"))
        else:
           server.SimpleHTTPRequestHandler.do_GET(self)



def serve(destination, port, config):
    """Run a simple web server."""
    if os.path.exists(destination):
        pass
    elif os.path.exists(config):
        settings = read_settings(config)
        destination = settings.get('destination')
        if not os.path.exists(destination):
            sys.stderr.write(
                f"The '{destination}' directory doesn't exist, maybe try building"
                " first?\n"
            )
            sys.exit(1)
    else:
        sys.stderr.write(
            f"The {destination} directory doesn't exist "
            f"and the config file ({config}) could not be read.\n"
        )
        sys.exit(2)

    print(f'DESTINATION : {destination}')
    os.chdir(destination)
    #Handler = server.SimpleHTTPRequestHandler
    Handler = PouServerHandler
    httpd = socketserver.TCPServer(("", port), Handler, False)
    print(f" * Running on http://127.0.0.1:{port}/")

    try:
        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nAll done!')




def readConfig():
    #Funkce převzata z projektu sigal -> soubor settings.py
    filename="sigal.conf.py"
    settings_path = os.path.dirname(filename)
    global config

    with open(filename) as f:
        code = compile(f.read(), filename, 'exec')
        exec(code, config)
    #print("Config:"+str(config))


def photoServer(port):
	readConfig()
	if not 'destination' in  config:
		config['destination']="_build"
	config["runDir"]=os.getcwd()+"/"
	serve(config['destination'],port,"nic")

def main():
	photoServer()
	


if __name__ == "__main__":
    main()


