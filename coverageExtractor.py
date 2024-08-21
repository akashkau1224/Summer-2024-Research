import xml.etree.ElementTree as ET
import json

class coverageExtractor:

    def iter_code_flows(self, sarif_json):
        """
        Iterate through the code flows within a SARIF json obtained from running path queries with CodeQL
        """
        for (i, result) in enumerate(sarif_json["runs"][0]["results"]):
            if "codeFlows" not in result: continue
            code_flows = result["codeFlows"]
            for (j, code_flow) in enumerate(code_flows):
                yield (i, j, code_flow)

    def iter_code_flows_for_query(self, sarif_json):
        for (i, j, code_flow) in self.iter_code_flows(sarif_json):
            thread_flow = code_flow["threadFlows"][0]
            locations = thread_flow["locations"]
            path_locations = []
            for loc in locations:
                try:
                    file_url = loc["location"]["physicalLocation"]["artifactLocation"]["uri"]
                    region = loc["location"]["physicalLocation"]["region"]
                    start_line = region["startLine"]
                    start_column = region["startColumn"] if "startColumn" in region else 0
                    end_line = start_line if "endLine" not in region else region["endLine"]
                    end_column = region["endColumn"]
                    message = loc["location"]["message"]["text"]
                    path_locations.append({
                        "file_url": file_url,
                        "start_line": start_line,
                        "start_column": start_column,
                        "end_line": end_line,
                        "end_column": end_column,
                        "message": message
                    })
                except Exception as e:
                    self.project_logger.error(f"Error extracting location: {e}")
                    continue
            yield (i, j, path_locations)

    # Takes SARIF JSON filepath for corresponding CVE as input along with the alarm and codeflow corresponding to the visualizer we are looking at
    def parseSarif(self, sarifJsonFilepath, alarm, codeFlow):
        with open(sarifJsonFilepath, 'r') as file:
            data = json.load(file)
        iterator = self.iter_code_flows_for_query(data)
        splitTrace = []
        for (i, j, pathLocations) in iterator:
            if i == alarm and j == codeFlow:
                for location in pathLocations:
                    className = location["file_url"].split('/')[-1]
                    lineNumber = location["start_line"]
                    methodName = ""
                    splitTrace.append([className, lineNumber, methodName])
        
        return splitTrace

    # Trace formatted with each line as a step of the trace 
    # Each line should be formatted as "the trace step #line number of the trace step"
    def splitTrace(self, trace):
        splitTrace = trace.split('\n')

        if splitTrace[0].isspace() or splitTrace[0] == '':
            splitTrace.pop(0)
        if splitTrace[-1].isspace() or splitTrace[-1] == '':
            splitTrace.pop(-1)

        for i in range(len(splitTrace)):
            lineNumber = splitTrace[i].split("#")[-1]
            className = splitTrace[i].split('[')[1].split(']')[0]
            className = className.split(':')[0]
            methodName = splitTrace[i].split('(')[0].split(' ')[-1]
            splitTrace[i] = [className, lineNumber, methodName]
        return splitTrace


    # Given the xml file, class, and a line to look for, checks if the line is covered
    def findLine(self, root, traceFile, traceLine):
        try:
            for file in root.findall('.//sourcefile'):
                if file.get('name') == traceFile:
                    for line in file.findall('.//line'):
                        if line.get('nr') == str(traceLine):
                            # Checks the number of hits this line recieved
                            return int(line.get('ci')) > 0 
            return False
        except ET.ParseError as e:
            print(f"Error parsing the XML file: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Given an xml file, class, and a method name, checks if the method is hit by the test case
    def findMethod(self, root, traceFile, traceMethod):
        # Removes .java or other suffix
        traceClass = traceFile.split('.')[0]
        try:
            for package in root.findall('.//package'):
                for classElem in package.findall('.//class'):
                    # Checks outer class name rather than inner class
                    if classElem.get('name').split('/')[-1].split('$')[0] == traceClass:
                        for method in classElem.findall('.//method'):
                            # Checks either the method name is the same or if the method is a constructor
                            if method.get('name') == traceMethod or (classElem.get('name').split('$')[-1] == traceMethod and "init" in method.get('name')):
                                for counter in method.findall('.//counter'):
                                    counter_type = counter.get('type').lower()
                                    covered = int(counter.get('covered'))
                                    # Returns true only if the number of lines in the method is greater than zero
                                    if counter_type == 'method' and covered > 0:
                                        return True
                                return False
            return False
        except ET.ParseError as e:
            print(f"Error parsing the XML file: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Returns a list of Booleans whether that respective step of the trace was covered by the test case
    # xmlFile is the xml file path and traceList is generated using the parseSarif method
    def percentTrace(self, traceList, xmlFile) -> list[bool]:
        returnList = []
        try:
            tree = ET.parse(xmlFile)
            root = tree.getroot()
            for i in range(len(traceList)):
                traceClass = traceList[i][0]
                traceLine = traceList[i][1]
                traceMethod = traceList[i][2]
                lineOutput = self.findLine(root, traceClass, traceLine)
                returnList.append(lineOutput)
                # methodOutput = self.findMethod(root, traceClass, traceMethod)
                # Checks if the trace step is a covered method only if the line isn't shown as covered
                # if lineOutput:
                #     returnList.append(lineOutput)
                # else:
                #     returnList.append(methodOutput)

            return returnList

        except ET.ParseError as e:
            print(f"Error parsing the XML file: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def formattedOutput(self, booleanList):
        res = "See function.txt for details about steps\n"
        for i in range(len(booleanList)):
            if booleanList[i]:
                res += "LLM Test case covered step " + str(i + 1) + " \n"
            else:
                res += "LLM Test case did not cover step " + str(i + 1) + " \n"
        return res


def success(booleanList):
    if len(booleanList) >= 6:
        return(booleanList[0] or booleanList[1] or booleanList[2]) and (booleanList[-3] or booleanList[-2] or booleanList[-1])
    else:
        return booleanList[0] and booleanList[-1]

### OLD CODE ###

    #  Split trace that works with the post processed trace appended with line numbers
    #  def splitTrace(self, trace):
    #         splitTrace = trace.split('\n')

    #         if splitTrace[0].isspace() or splitTrace[0] == '':
    #             splitTrace.pop(0)
    #         if splitTrace[-1].isspace() or splitTrace[-1] == '':
    #             splitTrace.pop(-1)

    #         for i in range(len(splitTrace)):
    #             lineNumber = splitTrace[i].split("#")[-1]
    #             className = splitTrace[i].split('[')[1].split(']')[0]
    #             className = className.split(':')[0]
    #             methodName = splitTrace[i].split('(')[0].split(' ')[-1]
    #             splitTrace[i] = [className, lineNumber, methodName]
    #         return splitTrace


    # def splitTrace(self, trace):
        # splitTrace = trace.split('\n')
        # returnList = []
        
        # if splitTrace[0].isspace() or splitTrace[0] == '':
        #     splitTrace.pop(0)
        # if splitTrace[-1].isspace() or splitTrace[-1] == '':
        #     splitTrace.pop(-1)
        
        # for i in range(len(splitTrace)):
        #     elem = splitTrace[i].split('[')
        #     elemTwo = elem[1].split(']')
        #     classMethod = elemTwo[0]
        #     classMethodSplit = elemTwo[0].split(':')
        #     returnListClass = classMethodSplit[0]

        #     split = splitTrace[i].split('(')
        #     returnListMethod = split[0].split(' ')[-1]

        #     returnListLine = splitTrace[i].split("]: ")[-1]
            
        #     returnList.append([returnListClass, returnListMethod, returnListLine])

        # return returnList
    
    
    # def findMethod(self, root, traceClass, traceMethod):
    #     try:
    #         for package in root.findall('.//package'):
    #             for classElem in package.findall('class'):
    #                 if classElem.get('name').split('/')[-1].split('$')[0] == traceClass:
    #                     for method in classElem.findall('method'):
    #                         if method.get('name') == traceMethod or (classElem.get('name').split('$')[-1] == traceMethod and "init" in method.get('name')):
    #                             print(traceClass + ":" + traceMethod)
    #                             for counter in method.findall('counter'):
    #                                 counter_type = counter.get('type').lower()
    #                                 covered = int(counter.get('covered'))

    #                                 if counter_type == 'method' and covered > 0:
    #                                     print("True")
    #                                     return 2
    #                             return 1
    #         return 0
    #     except ET.ParseError as e:
    #         print(f"Error parsing the XML file: {e}")
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

    # def getLineNumber(repoPath, fileName, lineContent):
    #     sourceFile = ""
    #     for root, dirs, files in os.walk(repoPath):
    #         if fileName in files:
    #             sourceFile = os.path.join(root, fileName)
    #         else:
    #             print("error")
    #     with open(sourceFile, 'r') as file:
    #         for lineNumber, content in enumerate(file, start=1):
    #             if content.strip() == lineContent.strip():
    #                 return lineNumber
    #     return None 


    # def percentTrace(self, traceList, xmlFile):
        # total = len(traceList)
        # try:
        #     tree = ET.parse(xmlFile)
        #     root = tree.getroot()
        #     count = 0
        #     for i in range(len(traceList)):
        #         traceClass = traceList[i][0].split('.')[0]
        #         traceMethod = traceList[i][1]
        #         output = self.findMethod(root, traceClass, traceMethod)
        #         if output == 2:
        #             count += 1
        #         elif output == 0:
        #             #find line

        #     print(len(traceList))
        #     print(count)
        #     return count / total

        # except ET.ParseError as e:
        #     print(f"Error parsing the XML file: {e}")
        # except Exception as e:
        #     print(f"An error occurred: {e}")

        # def findLine(self, root, traceClass, traceLine):
        #using getLineNumber find if the xml has covered this line
        # try:
            
            # for package in root.findall('.//package'):
            #     for classElem in package.findall('.//class'):
            #         if classElem.get('name').split('/')[-1].split('$')[0] == traceClass:
            #             for line in classElem.findall('.//line'):
            #                 print("got here")
            #                 if line.get("nr") == traceLine:
            #                     return True
        #     return False
        # except ET.ParseError as e:
        #     print(f"Error parsing the XML file: {e}")
        # except Exception as e:
        #     print(f"An error occurred: {e}")
