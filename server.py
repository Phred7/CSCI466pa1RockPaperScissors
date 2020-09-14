import email
import io
import mimetypes
import os
import posixpath
import shutil
import urllib
import datetime
import html
import sys
import array
from io import BytesIO
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, HTTPServer, BaseHTTPRequestHandler


#Accept a play message, no player can make +one different plays

#Accept a query for a play result and reply with result

#Accept a query for game score and reply with result

#Accept a game request message and delete plays that make up the game
#Both players must request a reset
#HTTP does not store anything in mem between requests, must keep track of who sent reset requests

class Game():
        def __init__(self, logPath, dataPath):
                self.log = logPath
                self.onDisk = dataPath
                self.clients = [-1, -1] 
                self.score = [0, 0] #wins from each game
                self.matches = 0
                self.numClients = 0
                self.results = [0, 0] #most recent results
                self.plays = [-1, -1] #r, p or s logically=to 1,2 or 3
                self.tied = False
                self.reset = [False, False]
                self.writeLog("ip","clientIden","request","data","status")
                self.writeData()


                
        def writeLog(self, ip, source, requestType, data, status):
                out = str(ip) + "," + str(source) + "," + str(requestType) + "," + str(data) + "," + str(status) + "\n"
                self.f = open(self.log, "a+")
                self.f.write(out)
                self.f.close()



        def writeData(self):
                self.f = open(self.onDisk, "w+")
                self.f.write("client0, client1, numClients, score0, score1, matches, results0, results1, plays0, plays1, tied, reset0, reset1\n")
                self.f.write(str(self.clients[0]) + "," + str(self.clients[1]) + "," + str(self.numClients) + "," + str(self.score[0]) + "," + str(self.score[1]) + "," + str(self.matches) + "," + str(self.results[0]) + "," + str(self.results[1]) + "," + str(self.plays[0]) + "," + str(self.plays[1]) + "," + str(self.tied) + "," + str(self.reset[0]) + "," + str(self.reset[1]))
                self.f.close()


        def serializeData(self):
                self.f = open(self.onDisk, "r")
                line = ''
                for x in self.f:
                        x = x.split(',')
                        if(x[0] != 'client0'):
                                line = x
                self.clients[0] = int(line[0])
                self.clients[1] = int(line[1])
                self.numClients = int(line[2])
                self.score[0] = int(line[3])
                self.score[1] = int(line[4])
                self.matches = int(line[5])
                self.results[0] = int(line[6])
                self.results[1] = int(line[7])
                self.plays[0] = int(line[8])
                self.plays[1] = int(line[9])
                self.tied = False if line[10] == "False" else True
                self.reset[0] = False if line[11] == "False" else True
                self.reset[1] = False if line[12] == "False" else True
                self.f.close()



        def resetGame(self):
                self.writeLog("clients", "clients", "gameReset", ("clients " + str(self.clients[0]) + " " + str(self.clients[1]) + "both requested a game reset"), "200")
                self.score = [0, 0]
                self.matches = 0
                self.results = [0, 0]
                self.plays = [-1, -1]
                self.tied = False
                self.reset = [False, False]



        def getResults(self, ip, source):
                self.serializeData()
                index = -1
                response = ""
                for i in range(len(self.clients)):
                        if(int(source) == int(self.clients[i])):
                                index = i
                other = 0 if index == 1 else 1

                if(self.results[index] == 1):
                        response += "You won match " + str(self.matches) + "!"
                elif(self.tied):
                        response += "This match tied; send another move"
                elif(self.results[index] == self.results[other]):
                        response += "Results for match " + str(self.matches) + " have not been determined yet"
                else:
                        response += "You lost match " + str(self.matches)
                
                if(self.numClients == 0):
                        errCode = 500
                        err = "Server restart occured, restart client"
                        self.writeLog(ip, source, "GET:results", str(err), errCode)
                        return [errCode, err]

                self.writeLog(ip, source, "GET:results", str(response), 200)
                self.writeData()
                return [200, response]



        def getScore(self, ip, source):
                self.serializeData()
                index = -1
                response = ""
                for i in range(len(self.clients)):
                        if(int(source) == int(self.clients[i])):
                                index = i
                other = 0 if index == 1 else 1

                if(self.score[index] > self.score[other]):
                        response += "You are currently winning: "
                elif(self.score[index] < self.score[other]):
                        response += "You are currently behind: "
                else:
                        response += "You are currently tied: "
                
                if(index == 0):
                        response += ("[" + str(self.score[0]) + ":" + str(self.score[1]) + "]")
                else:
                        response += ("[" + str(self.score[1]) + ":" + str(self.score[0]) + "]")

                if(self.numClients == 0):
                        errCode = 500
                        err = "Server restart occured: restart client"
                        self.writeLog(ip, source, "GET:results", str(err), errCode)
                        return [errCode, err]                

                self.writeLog(ip, source, "GET:score", str(response), 200)
                self.writeData()
                return [200, response]



        def putResetRequest(self, ip, source):
                self.serializeData()
                index = -1
                response = ""
                for i in range(len(self.clients)):
                        if(int(source) == int(self.clients[i])):
                                index = i
                other = 0 if index == 1 else 1

                if(self.reset[index] == True):
                        response = 'reset already requested'
                        return [200, response]

                self.reset[index] = True
                response = 'reset request successful'

                if(self.reset[index] and self.reset[other]):
                        self.resetGame()
                        response += ': game reset'
                else:
                        response += (': waiting on client ' + str(self.clients[other]))

                self.writeLog(ip, source, "PUT:reset", str(response), 200)
                self.writeData()
                return [200, response]



        def putPlay(self, ip, source, play):
                self.serializeData()
                index = -1
                response = ""
                for i in range(len(self.clients)):
                        if(int(source) == int(self.clients[i])):
                                index = i
                other = 0 if index == 1 else 1

                if(self.plays[index] != -1):
                        response = "play failed"
                        response += ("; waiting for client " + str(self.clients[other]) + " to play")
                        return [200, response]

                if(play == 'rock'):
                        self.plays[index] = 1
                elif(play == 'paper'):
                        self.plays[index] = 2
                elif(play == 'scizors'):
                        self.plays[index] = 3
                else:
                        return [400, str('This play does not exist: ' + str(play))]

                response = 'successfully played: ' + play

                if(self.plays[other] == -1):
                        response += ("; waiting for client " + str(self.clients[other]) + " to play")
                else:
                        self.results = [0, 0]
                        if(self.plays[0] == self.plays[1]):
                                response += "; match tied"
                                self.plays = [-1, -1]
                                self.tied = True
                        else:
                                if(self.plays[0] == 1 and self.plays[1] == 2):
                                        self.incriment(1)
                                elif(self.plays[0] == 1 and self.plays[1] == 3):
                                        self.incriment(0)
                                elif(self.plays[0] == 2 and self.plays[1] == 1):
                                        self.incriment(0)
                                elif(self.plays[0] == 2 and self.plays[1] == 3):
                                        self.incriment(1)
                                elif(self.plays[0] == 3 and self.plays[1] == 1):
                                        self.incriment(1)
                                elif(self.plays[0] == 3 and self.plays[1] == 2):
                                        self.incriment(0)
                                else:
                                        return [500, 'Unrecoverable Server Error: Restart Required']
                                self.tied = False
                                self.plays = [-1, -1]
                                response += "; match results availible"
                
                self.writeLog(ip, source, "PUT:play", str(response), 200)
                self.writeData()
                return [200, response]

        def incriment(self, winner):
                self.matches += 1
                self.score[winner] += 1
                if(winner == 0):
                        self.results = [1, 0]
                else:
                        self.results = [0, 1]

        def initClientConnection(self, ip, source):
                self.serializeData()
                if(int(self.clients[0]) == -1):
                        self.clients[0] = source
                elif(int(self.clients[1]) == -1):
                        self.clients[1] = source
                else:
                        self.writeLog(ip, source, "GET:init", "new connection refused: too many clients", 409)
                        return 409
                out = str(ip) + ", " + str(source) + ", GET:init, new connection\n"
                self.writeLog(ip, source, "GET:init", "new connection", 200)
                self.numClients += 1
                self.writeData()
                return 200



        def disconnectClient(self, ip, source):
                self.serializeData()
                self.clients[0] = -1 if self.clients[0] == source else self.clients[0]
                self.clients[1] = -1 if self.clients[1] == source else self.clients[1]

                if(self.clients[0] == -1 and self.clients[1] == -1):
                        self.resetGame()
                
                if(self.clients[0] == source or self.clients[1] == source):
                        errCode = 503
                        err = "Disconnection Unsuccessful"
                        return [errCode, err]
                self.numClients -= 1
                self.numClients = 0 if self.numClients < 0 else self.numClients
                self.writeLog(ip, source, "PUT:disCon", "remove connection", 200)
                self.writeData()
                return [200, "Disconnected"]

        def __str__(self):
                return str(self.score) + ", " + str(self.clients)


        
log = "log.csv"
onDisk = "data.csv"
rps = Game(log, onDisk)



class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
        """Simple HTTP request handler with GET and HEAD commands.

        This serves files from the current directory and any of its
        subdirectories.  The MIME type for files is determined by
        calling the .guess_type() method.

        The GET and HEAD requests are identical except that the HEAD
        request omits the actual contents of the file.

        """
        
        server_version = "RPS_HTTP_Server/"
        
        def __init__(self, *args, directory=None, **kwargs):
                self.game = rps
                if directory is None:
                        directory = os.getcwd()
                self.directory = directory
                super().__init__(*args, **kwargs)


        
        def do_GET(self):
                """Serve a GET request."""
                path = self.path
                path = path.split('?')
                path = path[1]
                path = path.split('&')
                currClient = path[1]
                currClient = currClient.split('=')
                path = path[0]
                path = path.split('=')
                path = {path[0]:path[1], currClient[0]:currClient[1]}
                client = int(path.get('iden'))
                hostIP = self.client_address[0]
                
                if((path.get('type') == 'init') and (int(path.get('iden')) == -1)):
                        sourcePort = self.client_address[1]
                        status = self.game.initClientConnection(hostIP, sourcePort)
                        self.send_response(status)
                        self.end_headers()
                        sourcePort = bytes(str(sourcePort), 'utf-8')
                        response = BytesIO()
                        response.write(sourcePort)
                        self.wfile.write(response.getvalue())
                elif(path.get('type') == 'results'):
                        status = self.game.getResults(hostIP,client)
                        response = status[1]
                        status = int(status[0])
                        self.send_response(status)
                        self.end_headers()
                        data = bytes(str(response), 'utf-8')
                        response = BytesIO()
                        response.write(data)
                        self.wfile.write(response.getvalue())
                elif(path.get('type') == 'score'):               
                        status = self.game.getScore(hostIP, client)
                        response = status[1]
                        status = int(status[0])
                        self.send_response(status)
                        self.end_headers()
                        data = bytes(str(response), 'utf-8')
                        response = BytesIO()
                        response.write(data)
                        self.wfile.write(response.getvalue())
                else:
                        self.send_response(501)
                        self.end_headers()
                        self.wfile.write(b'This type of GET request is not supported. ')         
                
                                   

        def do_PUT(self):
                """Server a PUT request."""
                dataLength = int(self.headers['Content-Length'])
                data = self.rfile.read(dataLength)
                pData = data.decode('utf-8')
                pData = pData.split('&')
                reset = pData[0]
                reset = reset.split('=')
                play = pData[1]
                play = play.split('=')
                iden = pData[2]
                iden = iden.split('=')
                pData = {'reset' : reset[1], 'play' : play[1], 'iden' : iden[1]}
                hostIP = self.client_address[0]

                if(str(pData.get('play')) == 'disCon'):
                        status = self.game.disconnectClient(hostIP, int(pData.get('iden')))
                        response = status[1]
                        status = int(status[0])
                        self.send_response(status)
                        self.end_headers()
                        data = bytes(str(response), 'utf-8')
                        response = BytesIO()
                        response.write(data)
                        self.wfile.write(response.getvalue())
                elif(str(pData.get('reset')) == 'True'):
                        status = self.game.putResetRequest(hostIP, int(pData.get('iden')))
                        response = status[1]
                        status = int(status[0])
                        self.send_response(status)
                        self.end_headers()
                        data = bytes(str(response), 'utf-8')
                        response = BytesIO()
                        response.write(data)
                        self.wfile.write(response.getvalue())
                elif(str(pData.get('play')) == 'rock'):
                        status = self.game.putPlay(hostIP, int(pData.get('iden')), str(pData.get('play')))
                        response = status[1]
                        status = int(status[0])
                        self.send_response(status)
                        self.end_headers()
                        data = bytes(str(response), 'utf-8')
                        response = BytesIO()
                        response.write(data)
                        self.wfile.write(response.getvalue())
                elif(str(pData.get('play')) == 'scizors'):
                        status = self.game.putPlay(hostIP, int(pData.get('iden')), str(pData.get('play')))
                        response = status[1]
                        status = int(status[0])
                        self.send_response(status)
                        self.end_headers()
                        data = bytes(str(response), 'utf-8')
                        response = BytesIO()
                        response.write(data)
                        self.wfile.write(response.getvalue())
                elif(str(pData.get('play')) == 'paper'):
                        status = self.game.putPlay(hostIP, int(pData.get('iden')), str(pData.get('play')))
                        response = status[1]
                        status = int(status[0])
                        self.send_response(status)
                        self.end_headers()
                        data = bytes(str(response), 'utf-8')
                        response = BytesIO()
                        response.write(data)
                        self.wfile.write(response.getvalue())
                else:
                        self.send_response(501)
                        self.end_headers()
                        response = BytesIO()
                        self.wfile.write(b'This type of PUT request is not supported. ')
                        response.write(b'Recieved: ')
                        response.write(data)
                        self.wfile.write(response.getvalue())


        
        def do_HEAD(self):
                """Serve a HEAD request."""
                f = self.send_head()
                if f:
                        f.close()
        
        def send_head(self):
                """Common code for GET and HEAD commands.

                This sends the response code and MIME headers.

                Return value is either a file object (which has to be copied
                to the outputfile by the caller unless the command was HEAD,
                and must be closed by the caller under all circumstances), or
                None, in which case the caller has nothing further to do.

                """
                
                path = self.translate_path(self.path)
                f = None
                if os.path.isdir(path):
                        parts = urllib.parse.urlsplit(self.path)
                        if not parts.path.endswith('/'):
                                # redirect browser - doing basically what apache does
                                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                                new_parts = (parts[0], parts[1], parts[2] + '/',
                                             parts[3], parts[4])
                                new_url = urllib.parse.urlunsplit(new_parts)
                                self.send_header("Location", new_url)
                                self.end_headers()
                                return None
                        for index in "index.html", "index.htm":
                                index = os.path.join(path, index)
                                if os.path.exists(index):
                                        path = index
                                        break
                        else:
                                return self.list_directory(path)
                ctype = self.guess_type(path)
                try:
                        f = open(path, 'rb')
                except OSError:
                        self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                        return None
                
                try:
                        fs = os.fstat(f.fileno())
                        # Use browser cache if possible
                        if ("If-Modified-Since" in self.headers
                                 and "If-None-Match" not in self.headers):
                                # compare If-Modified-Since and time of last file modification
                                try:
                                        ims = email.utils.parsedate_to_datetime(
                                                self.headers["If-Modified-Since"])
                                except (TypeError, IndexError, OverflowError, ValueError):
                                        # ignore ill-formed values
                                        pass
                                else:
                                        if ims.tzinfo is None:
                                                # obsolete format with no timezone, cf.
                                                # https://tools.ietf.org/html/rfc7231#section-7.1.1.1
                                                ims = ims.replace(tzinfo=datetime.timezone.utc)
                                        if ims.tzinfo is datetime.timezone.utc:
                                                # compare to UTC datetime of last modification
                                                last_modif = datetime.datetime.fromtimestamp(
                                                        fs.st_mtime, datetime.timezone.utc)
                                                # remove microseconds, like in If-Modified-Since
                                                last_modif = last_modif.replace(microsecond=0)
                                                
                                                if last_modif <= ims:
                                                        self.send_response(HTTPStatus.NOT_MODIFIED)
                                                        self.end_headers()
                                                        f.close()
                                                        return None
                        
                        self.send_response(HTTPStatus.OK)
                        self.send_header("Content-type", ctype)
                        self.send_header("Content-Length", str(fs[6]))
                        self.send_header("Last-Modified",
                                         self.date_time_string(fs.st_mtime))
                        self.end_headers()
                        return f
                except:
                        f.close()
                        raise
        
        def list_directory(self, path):
                """Helper to produce a directory listing (absent index.html).

                Return value is either a file object, or None (indicating an
                error).  In either case, the headers are sent, making the
                interface the same as for send_head().

                """
                try:
                        list = os.listdir(path)
                except OSError:
                        self.send_error(
                                HTTPStatus.NOT_FOUND,
                                "No permission to list directory")
                        return None
                list.sort(key=lambda a: a.lower())
                r = []
                try:
                        displaypath = urllib.parse.unquote(self.path,
                                                           errors='surrogatepass')
                except UnicodeDecodeError:
                        displaypath = urllib.parse.unquote(path)
                displaypath = html.escape(displaypath, quote=False)
                enc = sys.getfilesystemencoding()
                title = 'Directory listing for %s' % displaypath
                r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                         '"http://www.w3.org/TR/html4/strict.dtd">')
                r.append('<html>\n<head>')
                r.append('<meta http-equiv="Content-Type" '
                         'content="text/html; charset=%s">' % enc)
                r.append('<title>%s</title>\n</head>' % title)
                r.append('<body>\n<h1>%s</h1>' % title)
                r.append('<hr>\n<ul>')
                for name in list:
                        fullname = os.path.join(path, name)
                        displayname = linkname = name
                        # Append / for directories or @ for symbolic links
                        if os.path.isdir(fullname):
                                displayname = name + "/"
                                linkname = name + "/"
                        if os.path.islink(fullname):
                                displayname = name + "@"
                        # Note: a link to a directory displays with @ and links with /
                        r.append('<li><a href="%s">%s</a></li>'
                                 % (urllib.parse.quote(linkname,
                                                       errors='surrogatepass'),
                                    html.escape(displayname, quote=False)))
                r.append('</ul>\n<hr>\n</body>\n</html>\n')
                encoded = '\n'.join(r).encode(enc, 'surrogateescape')
                f = io.BytesIO()
                f.write(encoded)
                f.seek(0)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-type", "text/html; charset=%s" % enc)
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                return f
        
        def translate_path(self, path):
                """Translate a /-separated PATH to the local filename syntax.

                Components that mean special things to the local file system
                (e.g. drive or directory names) are ignored.  (XXX They should
                probably be diagnosed.)

                """
                # abandon query parameters
                path = path.split('?', 1)[0]
                path = path.split('#', 1)[0]
                # Don't forget explicit trailing slash when normalizing. Issue17324
                trailing_slash = path.rstrip().endswith('/')
                try:
                        path = urllib.parse.unquote(path, errors='surrogatepass')
                except UnicodeDecodeError:
                        path = urllib.parse.unquote(path)
                path = posixpath.normpath(path)
                words = path.split('/')
                words = filter(None, words)
                path = self.directory
                for word in words:
                        if os.path.dirname(word) or word in (os.curdir, os.pardir):
                                # Ignore components that are not a simple file/directory name
                                continue
                        path = os.path.join(path, word)
                if trailing_slash:
                        path += '/'
                return path
        
        def copyfile(self, source, outputfile):
                """Copy all data between two file objects.

                The SOURCE argument is a file object open for reading
                (or anything with a read() method) and the DESTINATION
                argument is a file object open for writing (or
                anything with a write() method).

                The only reason for overriding this would be to change
                the block size or perhaps to replace newlines by CRLF
                -- note however that this the default server uses this
                to copy binary data as well.

                """
                shutil.copyfileobj(source, outputfile)
        
        def guess_type(self, path):
                """Guess the type of a file.

                Argument is a PATH (a filename).

                Return value is a string of the form type/subtype,
                usable for a MIME Content-type header.

                The default implementation looks the file's extension
                up in the table self.extensions_map, using application/octet-stream
                as a default; however it would be permissible (if
                slow) to look inside the data to make a better guess.

                """
                
                base, ext = posixpath.splitext(path)
                if ext in self.extensions_map:
                        return self.extensions_map[ext]
                ext = ext.lower()
                if ext in self.extensions_map:
                        return self.extensions_map[ext]
                else:
                        return self.extensions_map['']
        
        if not mimetypes.inited:
                mimetypes.init()  # try to read system mime.types
        extensions_map = mimetypes.types_map.copy()
        extensions_map.update({
                '': 'application/octet-stream',  # Default
                '.py': 'text/plain',
                '.c': 'text/plain',
                '.h': 'text/plain',
        })



def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
        port = 8000;
        if(len(sys.argv) == 2):
                port = int(sys.argv[1])
                #print(sys.argv[1])
                
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print("\nServing on port " + str(port) + "\n")
        try:
                httpd.serve_forever()
        except:
                print("\nServer Shutting Down...")



if __name__ == "__main__":
        run(HTTPServer, MyHTTPRequestHandler)


