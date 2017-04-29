import urllib2
import csv
import BeautifulSoup as BS
import re
import contextlib
import ssl

HEADER = ["Source URL", "Source URL Status Code", "Extracted URL",
          "Anchor Text", "Rel Attributes"]


def parse_webpage(status_code, data_stream, csv):
    anchors = BS.BeautifulSoup(data_stream).findAll(
        "a", href=re.compile("chegg\.com/"))
    for anchor in anchors:
        text = anchor.text.strip().encode('utf-8')
        href = anchor['href'].encode('utf-8')

        rel = ""
        if anchor.has_key('rel'):
            rel = anchor['rel']

        yield [href, text, rel]


def parse_input(_file, csv):

    for element in _file:
        if ".pdf" in element:
                csv.writerow([element, "-", "-", "-", "-"])
        else:
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                element = element.strip('\r\n')
                req = urllib2.Request(element)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req, context=ctx)
            except urllib2.HTTPError, e:
                error = element, e.code
                print error
                status_code = e.code
                csv.writerow([element, status_code, "-", "-", "-"])
            except urllib2.URLError, e:
                print "{0} -> {1}".format(element, e)
                status_code = 0
                csv.writerow([element, status_code, "-", "-", "-"])
            else:
                status_code = response.getcode()
                data_stream = response.read()
                dataset = parse_webpage(status_code, data_stream, csv)
                if "chegg.com" in data_stream:
                    for item in dataset:
                        print element, status_code
                        csv.writerow([element, status_code] + item)
                        contextlib.closing(response)
                else:
                    nolinks = element, status_code
                    print nolinks
                    csv.writerow([element, status_code, "-", "-", "-"])
                    contextlib.closing(response)

if __name__ == '__main__':
    with open("nicelist.txt", "r") as url_file, \
            open("second-results4.csv", "wb") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(HEADER)
        parse_input(url_file, writer)