from burp import IBurpExtender
from burp import IScannerCheck
from burp import IScanIssue
from array import array
import random

GREP_STRING = "html"
GREP_STRING_BYTES = bytearray(GREP_STRING)
INJ_TEST = bytearray("|")
INJ_ERROR = "Unexpected pipe"
INJ_ERROR_BYTES = bytearray(INJ_ERROR)
QUOTES = [
          '"I am so clever that sometimes I don\'t understand a single word of what I am saying." Oscar Wilde', 
          '"Optimist: you are."', 
          '"Always take notes, because i don\'t"', 
          '"Remember to breath from time to time, it\'s good for your health"', 
          '"Focus on one thing, it\'s likely not worth it"', 
          '"I got you something! No quotes for you GO BACK TO WORK"', 
          '"A banana"'
          ]
class BurpExtender(IBurpExtender, IScannerCheck):

    #
    # implement IBurpExtender
    #

    def registerExtenderCallbacks(self, callbacks):
        # keep a reference to our callbacks object
        self._callbacks = callbacks

        # obtain an extension helpers object
        self._helpers = callbacks.getHelpers()

        # set our extension name
        callbacks.setExtensionName("Imposteserum")

        # register ourselves as a custom scanner check
        callbacks.registerScannerCheck(self)
        print ('Lets find some crits shall we ;)')
    # helper method to search a response for occurrences of a literal match string
    # and return a list of start/end offsets

    def _get_matches(self, response, match):
        matches = []
        start = 0
        reslen = len(response)
        matchlen = len(match)
        while start < reslen:
            start = self._helpers.indexOf(response, match, True, start, reslen)
            if start == -1:
                break
            matches.append(array('i', [start, start + matchlen]))
            start += matchlen

        return matches

    #
    # implement IScannerCheck
    #

    def doPassiveScan(self, baseRequestResponse):
        # look for matches of our passive check grep string
        matches = self._get_matches(baseRequestResponse.getResponse(), GREP_STRING_BYTES)
        if (len(matches) == 0):
            return None

        # report the issue
        return [CustomScanIssue(
            baseRequestResponse.getHttpService(),
            self._helpers.analyzeRequest(baseRequestResponse).getUrl(),
            [self._callbacks.applyMarkers(baseRequestResponse, None, matches)],
            random.choice(QUOTES),
            "Just a random extension don't mind me ;)",
            "Information")]

    # def doActiveScan(self, baseRequestResponse, insertionPoint):
    #     # make a request containing our injection test in the insertion point
    #     checkRequest = insertionPoint.buildRequest(INJ_TEST)
    #     checkRequestResponse = self._callbacks.makeHttpRequest(
    #             baseRequestResponse.getHttpService(), checkRequest)

    #     # look for matches of our active check grep string
    #     matches = self._get_matches(checkRequestResponse.getResponse(), INJ_ERROR_BYTES)
    #     if len(matches) == 0:
    #         return None

    #     # get the offsets of the payload within the request, for in-UI highlighting
    #     requestHighlights = [insertionPoint.getPayloadOffsets(INJ_TEST)]

    #     # report the issue
    #     return [CustomScanIssue(
    #         baseRequestResponse.getHttpService(),
    #         self._helpers.analyzeRequest(baseRequestResponse).getUrl(),
    #         [self._callbacks.applyMarkers(checkRequestResponse, requestHighlights, matches)],
    #         "Pipe injection",
    #         "Submitting a pipe character returned the string: " + INJ_ERROR,
    #         "High")]

    def consolidateDuplicateIssues(self, existingIssue, newIssue):
        # This method is called when multiple issues are reported for the same URL 
        # path by the same extension-provided check. The value we return from this 
        # method determines how/whether Burp consolidates the multiple issues
        # to prevent duplication
        #
        # Since the issue name is sufficient to identify our issues as different,
        # if both issues have the same name, only report the existing issue
        # otherwise report both issues
        if existingIssue.getIssueName() == newIssue.getIssueName():
            return -1

        return 0

#
# class implementing IScanIssue to hold our custom scan issue details
#
class CustomScanIssue (IScanIssue):
    def __init__(self, httpService, url, httpMessages, name, detail, severity):
        self._httpService = httpService
        self._url = url
        self._httpMessages = httpMessages
        self._name = name
        self._detail = detail
        self._severity = severity

    def getUrl(self):
        return self._url

    def getIssueName(self):
        return self._name

    def getIssueType(self):
        return 0

    def getSeverity(self):
        return self._severity

    def getConfidence(self):
        return "Certain"

    def getIssueBackground(self):
        pass

    def getRemediationBackground(self):
        pass

    def getIssueDetail(self):
        return self._detail

    def getRemediationDetail(self):
        pass

    def getHttpMessages(self):
        return self._httpMessages

    def getHttpService(self):
        return self._httpService
