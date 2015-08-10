import ntpath
import olefile
import os
import sys


class Bupectomy(object):

    def __init__(self):
        self.details = None
        self.file_0 = None
        self.orig_filename = None

    def filecheck(self, bup):
        file_exists = os.path.exists(bup)

        if file_exists:
            olecheck = olefile.isOleFile(bup)
        else:
            sys.exit("\n[-] File not found\n")

        if olecheck == False:
            sys.exit("[-] Not a valid .bup file")

    def extractfiles(self, bup):
        ole = olefile.OleFileIO(bup)
        
        try:
            self.details = ole.openstream('Details').read()
            self.file_0 = ole.openstream('File_0').read()
        except Exception, e:
            print "[-] Unable to extract files from the bup"
            print e

    def single_byte_xor(self, buf):
        # taken from xortools.py

        key = ord('\x6a')
        out = ''
        for i in buf:
            out += chr(ord(i) ^ key)
        return out

    def parsedetails(self, detailsfile):

        # Not done
        # More to come here

        for item in self.details.splitlines():
            if "OriginalName" in item:
                self.orig_filename = ntpath.basename(item)


    def writefiles(self, buf, dirname, filename):

        details = os.path.join(dirname, filename)

        try:
            with open(os.path.join(dirname, filename), "w") as f:
                f.write(buf)
        except Exception, e:
            sys.exit(e)



class VirusTotal(object):
    def __init__(self):
        self.apikey = None

        if not self.apikey:
            sys.exit("[-] No VirusTotal API key provided")
            
        self.baseurl = "https://www.virustotal.com/vtapi/v2"
        self.vendor = None

    def httprequest(self, method, uri, payload):

        if method == "post":

            try:
                req = requests.post(self.baseurl + uri, data=payload)
                if "content-length" in req.headers:
                    sys.exit("[-] Too many API requests")
            except requests.ConnectionError as e:
                sys.exit(e)

            return json.loads(req.content)

    def fileresults(self, filepath):
        filehash = self.filehash(filepath)
        payload = {"resource": filehash, "apikey": self.apikey}
        self.vtcontent = self.httprequest("post", "/file/report", payload)
        return self.vtcontent

    def responsecode(self, responsecode):
        if responsecode == 0:
            print "[-] Response code '0' was returned by Virustotal API"
            print "[-] Either this resource was not found in VT's database, "\
                  "or the request was unsuccessful"
            sys.exit()

    def filehash(self, filepath):
        with open(filepath, "r") as f:
            filecontent = f.read()

        hashobj = hashlib.sha256(filecontent).hexdigest()
        return hashobj



if __name__ == "__main__":
    
    from argparse import ArgumentParser
    
    p = ArgumentParser()
    p.add_argument("bup", help="McAfee .bup file")
    p.add_argument("-d", "--details", help="Print detection details", action="store_true")
    p.add_argument("-o", "--output", help="Specify an output directory for the decoded files", action="store_true")
    p.add_argument("-v" "--vt", help="Check VirusTotal for this file in a previous submission", action="store_true")
    args = p.parse_args()

    if args.bup:
        b = Bupectomy()
        b.filecheck(args.bup)
        b.extractfiles(args.bup)
        b.details = b.single_byte_xor(b.details)
        b.parsedetails(b.details)
        b.file_0 = b.single_byte_xor(b.file_0)
    else:
        sys.exit("[-] .bup file not specified")

    if args.details:
        print b.details

    if args.output:
        b.writefiles(b.details, args.output, "details.txt")
        b.writefiles(b.file_0, args.output, b.orig_filename)

    if args.vt:
        vtresults = b.fileresults(args.bup)
        print vtresults

    if len(sys.argv) < 3:
        with open("details.txt", "w") as f:
            f.write(b.details)
        with open(b.orig_filename, "w") as f:
            f.write(b.file_0)

else:
    pass









