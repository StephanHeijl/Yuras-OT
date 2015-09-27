__author__ = 'stephan'
from collections import OrderedDict

class NumberConversion():
    """ This class provides number conversion for Dutch numbers. """

    numberNames = OrderedDict([
        (11,"elf"),
        (12,"twaalf"),
        (13,"dertien"),
        (14,"veertien"),
        (15,"vijftien"),
        (16,"zestien"),
        (17,"zeventien"),
        (18,"achtien"),
        (19,"negentien"),
        (1,"een"),
        (2,"twee"),
        (3,"drie"),
        (4,"vier"),
        (5,"vijf"),
        (6,"zes"),
        (7,"zeven"),
        (8,"acht"),
        (9,"negen"),
        (10,"tien"),
        (20,"twintig"),
        (30,"dertig"),
        (40,"veertig"),
        (50,"vijftig"),
        (60,"zestig"),
        (70,"zeventig"),
        (80,"tachtig"),
        (90,"negentig"),
        (100,"honderd"),
        (1000,"duizend"),
        (1000000,"miljoen"),
        (1000000000,"miljard")
    ])

    @staticmethod
    def convertNumberToText():
        pass

    @staticmethod
    def __arangeConstituents(constituents):
        multipliedComponents = []

        nconstituents = []
        skip = False
        # This step deals with merging all the "en" components
        for c in range(0,len(constituents),2):
            if skip:
                skip = False
                continue

            if constituents[c+1] == "*":
                nconstituents.append(constituents[c])
                nconstituents.append("*")
            else:
                nconstituents.append(constituents[c]+constituents[c+2])
                nconstituents.append("*")
                skip = True

        constituents = nconstituents
        print constituents
        # This step adds up all the now uniform components
        for c in range(0,len(constituents),2):
            print multipliedComponents
            try:
                constituents[c+2]
            except:
                if constituents[c] < constituents[c-2] or len(constituents) <= 2: # Add the last number to the components if it is less then the previous constituent
                    multipliedComponents.append( constituents[c] )
                break

            if constituents[c] < constituents[c+2]:
                multipliedComponents.append( constituents[c] * constituents[c+2] )
            else:
                if(c < 2 or constituents[c-2] > constituents[c] or c == len(constituents)-2):
                    multipliedComponents.append( constituents[c] )

        return multipliedComponents

    @staticmethod
    def convertTextToNumber(n):
        n = n.replace(" ", "")
        constituents = []
        while len(n) > 0:
            found = False
            for value, numberName in NumberConversion.numberNames.items():
                if n[:len(numberName)] == numberName:
                    constituents.append(value)
                    n = n[len(numberName):]
                    if not n.startswith("en"):
                        constituents.append("*")

                    found = True
                    break
            if not found:
                if n.startswith("en"):
                    n = n[2:]
                    constituents.append("+")
                else:
                    raise ValueError, "Not a valid Dutch number"

        if len(constituents) < 3:
            return constituents[0]

        print constituents

        multipliedComponents = NumberConversion.__arangeConstituents(constituents)
        pMC = 0

        #while pMC == 0 or len(multipliedComponents) < pMC:
        #    print multipliedComponents
        #    multipliedComponents = NumberConversion.__arangeConstituents(constituents)
        #    pMC = len(multipliedComponents)
        print sum(multipliedComponents)

        return sum(multipliedComponents)


def test_convertNumberToText():
    pass

def test_convertTextToNumber():
    assert NumberConversion.convertTextToNumber("vijf") == 5
    assert NumberConversion.convertTextToNumber("vijfentwintighonderd") == 2500
    assert NumberConversion.convertTextToNumber("drieentwintig") == 23
    assert NumberConversion.convertTextToNumber("vierhonderd") == 400
    assert NumberConversion.convertTextToNumber("zestien") == 16
    assert NumberConversion.convertTextToNumber("tweeduizendachthonderddrieenveertig") == 2843
    assert NumberConversion.convertTextToNumber("zestienmiljoentachtigduizendtweehonderdzesendertig") == 16080236
    assert NumberConversion.convertTextToNumber("honderdnegenentwintig") == 129
    assert NumberConversion.convertTextToNumber("tweemiljoenduizendtweehonderd") == 2001200

    #assert NumberConversion.convertTextToNumber("zevenhonderdachtentwintigduizend") == 728000
    #assert NumberConversion.convertTextToNumber("driehonderdzevenenveertig miljard zeshonderdvijfentwintig miljoen zevenhonderdachtentwintigduizend tweehonderdeenentwintig") == 347625728221


test_convertTextToNumber()