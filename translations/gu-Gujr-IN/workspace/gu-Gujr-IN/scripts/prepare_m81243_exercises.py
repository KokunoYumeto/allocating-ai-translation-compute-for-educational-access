"""Build source-bound Gujarati exercise and metadata fragments for A00 m81243.

No mathematical tokens, identifiers, source children, or source media links change.
The self-check image text is supplied separately for an accessible rendering.
"""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'gu-Gujr-IN' / 'translations'
SOURCE = ROOT / 'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81243.source.cnxml'
SHA = '396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b'
C = 'http://cnx.rice.edu/cnxml'
M = 'http://www.w3.org/1998/Math/MathML'
MD = 'http://cnx.rice.edu/mdml'
ET.register_namespace('', C)
ET.register_namespace('m', M)
ET.register_namespace('md', MD)

# Exact source text after whitespace normalization. These are human-written
# translations, not a generalized machine translation replacement procedure.
TEXT = {
    'Practice Makes Perfect': 'અભ્યાસથી નિપુણતા',
    'Identify Counting Numbers and Whole Numbers': 'ગણતરીની સંખ્યાઓ અને પૂર્ણ સંખ્યાઓ ઓળખો',
    'In the following exercises, determine which of the following numbers are': 'નીચેના અભ્યાસમાં આપેલી સંખ્યાઓમાંથી કઈ',
    'counting numbers': 'ગણતરીની સંખ્યાઓ',
    'whole numbers.': 'પૂર્ણ સંખ્યાઓ છે તે નક્કી કરો.',
    'Model Whole Numbers': 'પૂર્ણ સંખ્યાઓને નમૂના દ્વારા દર્શાવો',
    'In the following exercises, use place value notation to find the value of the number modeled by the': 'નીચેના અભ્યાસમાં સ્થાનકિંમતની લખાવટનો ઉપયોગ કરીને',
    'blocks.': 'ના ખંડોથી દર્શાવેલી સંખ્યાનું મૂલ્ય શોધો.',
    'base-10': 'આધાર-10',
    'An image consisting of three items. The first item is five squares of 100 blocks each, 10 blocks wide and 10 blocks tall. The second item is six horizontal rods containing 10 blocks each. The third item is 1 individual block.': 'ચિત્રમાં ત્રણ પ્રકારના ભાગ છે. પહેલા ભાગમાં પાંચ ચોરસ છે; દરેક ચોરસમાં 100 ખંડ છે, 10 ખંડ પહોળાઈમાં અને 10 ખંડ ઊંચાઈમાં. બીજા ભાગમાં છ આડી સળીઓ છે; દરેકમાં 10 ખંડ છે. ત્રીજા ભાગમાં 1 અલગ ખંડ છે.',
    'An image consisting of three items. The first item is three squares of 100 blocks each, 10 blocks wide and 10 blocks tall. The second item is eight horizontal rods containing 10 blocks each. The third item is 4 individual blocks.': 'ચિત્રમાં ત્રણ પ્રકારના ભાગ છે. પહેલા ભાગમાં ત્રણ ચોરસ છે; દરેક ચોરસમાં 100 ખંડ છે, 10 ખંડ પહોળાઈમાં અને 10 ખંડ ઊંચાઈમાં. બીજા ભાગમાં આઠ આડી સળીઓ છે; દરેકમાં 10 ખંડ છે. ત્રીજા ભાગમાં 4 અલગ ખંડ છે.',
    'An image consisting of two items. The first item is four squares of 100 blocks each, 10 blocks wide and 10 blocks tall. The second item is 7 individual blocks.': 'ચિત્રમાં બે પ્રકારના ભાગ છે. પહેલા ભાગમાં ચાર ચોરસ છે; દરેક ચોરસમાં 100 ખંડ છે, 10 ખંડ પહોળાઈમાં અને 10 ખંડ ઊંચાઈમાં. બીજા ભાગમાં 7 અલગ ખંડ છે.',
    'An image consisting of two items. The first item is six squares of 100 blocks each, 10 blocks wide and 10 blocks tall. The second item is 2 horizontal rods with 10 blocks each.': 'ચિત્રમાં બે પ્રકારના ભાગ છે. પહેલા ભાગમાં છ ચોરસ છે; દરેક ચોરસમાં 100 ખંડ છે, 10 ખંડ પહોળાઈમાં અને 10 ખંડ ઊંચાઈમાં. બીજા ભાગમાં 2 આડી સળીઓ છે; દરેકમાં 10 ખંડ છે.',
    'Identify the Place Value of a Digit': 'અંકની સ્થાનકિંમત ઓળખો',
    'In the following exercises, find the place value of the given digits.': 'નીચેના અભ્યાસમાં આપેલા અંકોની સ્થાનકિંમત શોધો.',
    'thousands': 'હજારનું સ્થાન',
    'hundreds': 'સોનું સ્થાન',
    'tens': 'દશકનું સ્થાન',
    'ten thousands': 'દસ હજારનું સ્થાન',
    'hundred thousands': 'સો હજારનું સ્થાન',
    'millions': 'મિલિયનનું સ્થાન',
    'Use Place Value to Name Whole Numbers': 'સ્થાનકિંમતનો ઉપયોગ કરીને પૂર્ણ સંખ્યાઓ શબ્દોમાં કહો',
    'In the following exercises, name each number in words.': 'નીચેના અભ્યાસમાં દરેક સંખ્યા શબ્દોમાં કહો.',
    'One thousand, seventy-eight': 'એક હજાર, અઠ્ઠોતેર',
    'Three hundred sixty-four thousand, five hundred ten': 'ત્રણસો ચોસઠ હજાર, પાંચસો દસ',
    'Five million, eight hundred forty-six thousand, one hundred three': 'પાંચ મિલિયન, આઠસો છેતાલીસ હજાર, એકસો ત્રણ',
    'Thirty seven million, eight hundred eighty-nine thousand, five': 'સાડત્રીસ મિલિયન, આઠસો નેવ્યાસી હજાર, પાંચ',
    'The height of Mount Rainier is': 'રેનિયર પર્વતની ઊંચાઈ',
    'feet.': 'ફૂટ છે.',
    'Fourteen thousand, four hundred ten': 'ચૌદ હજાર, ચારસો દસ',
    'The height of Mount Adams is': 'એડમ્સ પર્વતની ઊંચાઈ',
    'Seventy years is': 'સિત્તેર વર્ષમાં',
    'hours.': 'કલાક થાય છે.',
    'Six hundred thirteen thousand, two hundred': 'છસો તેર હજાર, બસો',
    'One year is': 'એક વર્ષમાં',
    'minutes.': 'મિનિટ થાય છે.',
    'The U.S. Census estimate of the population of Miami-Dade county was': 'અમેરિકાની વસ્તીગણતરી મુજબ માયામી-ડેડ કાઉન્ટીની વસ્તીનો અંદાજ હતો:',
    'Two million, six hundred seventeen thousand, one hundred seventy-six': 'બે મિલિયન, છસો સત્તર હજાર, એકસો છોતેર',
    'The population of Chicago was': 'શિકાગોની વસ્તી હતી:',
    'There are projected to be': 'આગામી પાંચ વર્ષમાં અમેરિકાની કૉલેજો અને યુનિવર્સિટીઓમાં',
    'college and university students in the US in five years.': 'વિદ્યાર્થીઓ હશે એવો અંદાજ છે.',
    'Twenty three million, eight hundred sixty-seven thousand': 'તેવીસ મિલિયન, આઠસો સડસઠ હજાર',
    'About twelve years ago there were': 'લગભગ બાર વર્ષ પહેલાં કેલિફોર્નિયામાં',
    'registered automobiles in California.': 'નોંધાયેલાં મોટર વાહનો હતાં.',
    'The population of China is expected to reach': 'ચીનની વસ્તી',
    'in': 'સુધી પહોંચવાનો અંદાજ છે, વર્ષ',
    'One billion, three hundred seventy-seven million, five hundred eighty-three thousand, one hundred fifty-six': 'એક બિલિયન, ત્રણસો સિત્તોતેર મિલિયન, પાંચસો ત્ર્યાસી હજાર, એકસો છપ્પન',
    'The population of India is estimated at': 'ભારતની વસ્તીનો અંદાજ',
    'as of July': 'છે, જુલાઈ',
    'Use Place Value to Write Whole Numbers': 'સ્થાનકિંમતનો ઉપયોગ કરીને પૂર્ણ સંખ્યાઓ અંકોમાં લખો',
    'In the following exercises, write each number as a whole number using digits.': 'નીચેના અભ્યાસમાં દરેક પૂર્ણ સંખ્યા અંકોમાં લખો.',
    'four hundred twelve': 'ચારસો બાર',
    'two hundred fifty-three': 'બસો ત્રેપન',
    'thirty-five thousand, nine hundred seventy-five': 'પાંત્રીસ હજાર, નવસો પંચોતેર',
    'sixty-one thousand, four hundred fifteen': 'એકસઠ હજાર, ચારસો પંદર',
    'eleven million, forty-four thousand, one hundred sixty-seven': 'અગિયાર મિલિયન, ચુમ્માલીસ હજાર, એકસો સડસઠ',
    'eighteen million, one hundred two thousand, seven hundred eighty-three': 'અઢાર મિલિયન, એકસો બે હજાર, સાતસો ત્ર્યાસી',
    'three billion, two hundred twenty-six million, five hundred twelve thousand, seventeen': 'ત્રણ બિલિયન, બસો છવ્વીસ મિલિયન, પાંચસો બાર હજાર, સત્તર',
    'eleven billion, four hundred seventy-one million, thirty-six thousand, one hundred six': 'અગિયાર બિલિયન, ચારસો એકોતેર મિલિયન, છત્રીસ હજાર, એકસો છ',
    'The population of the world was estimated to be seven billion, one hundred seventy-three million people.': 'વિશ્વની વસ્તીનો અંદાજ સાત બિલિયન, એકસો તોતેર મિલિયન લોકોનો હતો.',
    'The age of the solar system is estimated to be four billion, five hundred sixty-eight million years.': 'સૂર્યમંડળની ઉંમરનો અંદાજ ચાર બિલિયન, પાંચસો અડસઠ મિલિયન વર્ષ છે.',
    'Lake Tahoe has a capacity of thirty-nine trillion gallons of water.': 'ટાહો સરોવરમાં ઓગણચાલીસ ટ્રિલિયન ગૅલન પાણી સમાઈ શકે છે.',
    'The federal government budget was three trillion, five hundred billion dollars.': 'કેન્દ્ર સરકારનું બજેટ ત્રણ ટ્રિલિયન, પાંચસો બિલિયન ડૉલર હતું.',
    'Round Whole Numbers': 'પૂર્ણ સંખ્યાઓને નજીકની સ્થાનકિંમતમાં ફેરવો',
    'In the following exercises, round to the indicated place value.': 'નીચેના અભ્યાસમાં સંખ્યાઓને દર્શાવેલી સૌથી નજીકની સ્થાનકિંમતમાં ફેરવો.',
    'Round to the nearest ten:': 'સૌથી નજીકના દશકમાં ફેરવો:',
    'Round to the nearest hundred:': 'સૌથી નજીકના સોમાં ફેરવો:',
    'Round to the nearest thousand:': 'સૌથી નજીકના હજારમાં ફેરવો:',
    'Everyday Math': 'રોજિંદા જીવનમાં ગણિત',
    'Writing a Check': 'ચેક લખવો',
    'Jorge bought a car for': 'હોર્હેએ કાર ખરીદી. તેની કિંમત હતી:',
    'He paid for the car with a check. Write the purchase price in words.': 'તેણે કારની કિંમત ચેકથી ચૂકવી. ખરીદકિંમત શબ્દોમાં લખો.',
    'Twenty four thousand, four hundred ninety-three dollars': 'ચોવીસ હજાર, ચારસો ત્રાણું ડૉલર',
    'Marissa’s kitchen remodeling cost': 'મરિસાના રસોડાના નવીનીકરણનો ખર્ચ હતો:',
    'She wrote a check to the contractor. Write the amount paid in words.': 'તેણે કોન્ટ્રાક્ટરને ચેક લખી આપ્યો. ચૂકવેલી રકમ શબ્દોમાં લખો.',
    'Buying a Car': 'કાર ખરીદવી',
    'Round the price to the nearest:': 'કિંમતને નીચે દર્શાવેલી સૌથી નજીકની સ્થાનકિંમતમાં ફેરવો:',
    'ten dollars': 'દસ ડૉલર',
    'hundred dollars': 'સો ડૉલર',
    'thousand dollars': 'હજાર ડૉલર',
    'ten-thousand dollars': 'દસ હજાર ડૉલર',
    'Remodeling a Kitchen': 'રસોડાનું નવીનીકરણ',
    'Round the cost to the nearest:': 'ખર્ચને નીચે દર્શાવેલી સૌથી નજીકની સ્થાનકિંમતમાં ફેરવો:',
    'Population': 'વસ્તી',
    'The population of China was': 'ચીનની વસ્તી',
    'Round the population to the nearest:': 'વસ્તીને નીચે દર્શાવેલી સૌથી નજીકની સ્થાનકિંમતમાં ફેરવો:',
    'billion people': 'બિલિયન લોકો',
    'hundred-million people': 'સો મિલિયન લોકો',
    'million people': 'મિલિયન લોકો',
    'Astronomy': 'ખગોળશાસ્ત્ર',
    'The average distance between Earth and the sun is': 'પૃથ્વી અને સૂર્ય વચ્ચેનું સરેરાશ અંતર',
    'kilometers. Round the distance to the nearest:': 'કિલોમીટર છે. અંતરને નીચે દર્શાવેલી સૌથી નજીકની સ્થાનકિંમતમાં ફેરવો:',
    'hundred-million kilometers': 'સો મિલિયન કિલોમીટર',
    'ten-million kilometers': 'દસ મિલિયન કિલોમીટર',
    'million kilometers': 'મિલિયન કિલોમીટર',
    'Writing Exercises': 'લેખન અભ્યાસ',
    'In your own words, explain the difference between the counting numbers and the whole numbers.': 'ગણતરીની સંખ્યાઓ અને પૂર્ણ સંખ્યાઓ વચ્ચેનો તફાવત તમારા પોતાના શબ્દોમાં સમજાવો.',
    'Answers may vary. The whole numbers are the counting numbers with the inclusion of zero.': 'જવાબો જુદા હોઈ શકે છે. ગણતરીની સંખ્યાઓ સાથે શૂન્યનો સમાવેશ કરતાં પૂર્ણ સંખ્યાઓ મળે છે.',
    'Give an example from your everyday life where it helps to round numbers.': 'તમારા રોજિંદા જીવનમાંથી એવું ઉદાહરણ આપો જેમાં સંખ્યાઓને નજીકની સ્થાનકિંમતમાં ફેરવવાથી મદદ મળે.',
    'Self Check': 'સ્વમૂલ્યાંકન',
    'After completing the exercises, use this checklist to evaluate your mastery of the objectives of this section.': 'અભ્યાસ પૂરો કર્યા પછી આ વિભાગનાં શીખવાનાં લક્ષ્યો તમે કેટલાં સિદ્ધ કર્યાં તે જાણવા આ તપાસયાદીનો ઉપયોગ કરો.',
    "A self-assessment chart for students to rate their understanding of whole numbers, place value, and rounding skills with options: Confidently, With some help, or No-I don't get it!.": 'પૂર્ણ સંખ્યાઓ, સ્થાનકિંમત અને સંખ્યાઓને ગોળ કરવાની સમજનું મૂલ્યાંકન કરવા માટેનું કોષ્ટક. દરેક કૌશલ્ય માટે વિકલ્પો છે: વિશ્વાસપૂર્વક, થોડી મદદથી, અથવા ના—મને સમજાતું નથી!',
    'If most of your checks were...': 'જો તમે સૌથી વધુ નિશાની આ વિકલ્પમાં કરી હોય તો...',
    '…confidently. Congratulations! You have achieved the objectives in this section. Reflect on the study skills you used so that you can continue to use them. What did you do to become confident of your ability to do these things? Be specific.': '…વિશ્વાસપૂર્વક. અભિનંદન! તમે આ વિભાગનાં શીખવાનાં લક્ષ્યો સિદ્ધ કર્યાં છે. તમે અભ્યાસની કઈ રીતો અપનાવી તે વિચારો, જેથી આગળ પણ તેનો ઉપયોગ કરી શકો. આ કામો તમે કરી શકશો એવો વિશ્વાસ કેળવવા તમે શું કર્યું? ચોક્કસ રીતે જણાવો.',
    '…with some help. This must be addressed quickly because topics you do not master become potholes in your road to success. In math, every topic builds upon previous work. It is important to make sure you have a strong foundation before you move on. Whom can you ask for help? Your fellow classmates and instructor are good resources. Is there a place on campus where math tutors are available? Can your study skills be improved?': '…થોડી મદદથી. આ બાબતે જલદી ધ્યાન આપવું જરૂરી છે, કારણ કે જે વિષયો તમને બરાબર સમજાયા નથી તે તમારી સફળતાના માર્ગમાં અવરોધ બની શકે છે. ગણિતમાં દરેક વિષય અગાઉ શીખેલી બાબતો પર આધાર રાખે છે. આગળ વધતાં પહેલાં તમારો પાયો મજબૂત છે તેની ખાતરી કરવી જરૂરી છે. તમે કોની મદદ માગી શકો? તમારા સહાધ્યાયીઓ અને શિક્ષક મદદ કરી શકે છે. શું તમારી શિક્ષણસંસ્થામાં ગણિતનું માર્ગદર્શન આપનારા શિક્ષકો મળે એવી કોઈ જગ્યા છે? શું તમે અભ્યાસ કરવાની તમારી રીતો સુધારી શકો?',
    '…no—I don’t get it! This is a warning sign and you must not ignore it. You should get help right away or you will quickly be overwhelmed. See your instructor as soon as you can to discuss your situation. Together you can come up with a plan to get you the help you need.': '…ના—મને સમજાતું નથી! આ ચેતવણી છે અને તમારે તેને અવગણવી જોઈએ નહીં. તરત મદદ લો, નહીં તો ટૂંક સમયમાં અભ્યાસનો ભાર તમને વધુ લાગશે. તમારી સ્થિતિ વિશે વાત કરવા બને તેટલા વહેલા તમારા શિક્ષકને મળો. તમને જરૂરી મદદ મળે તે માટે તમે બંને સાથે મળીને યોજના બનાવી શકો છો.',
}

META = {
    'Introduction to Whole Numbers': 'પૂર્ણ સંખ્યાઓનો પરિચય',
    'By the end of this section, you will be able to:': 'આ વિભાગના અંતે તમે:',
    'Identify counting numbers and whole numbers': 'ગણતરીની સંખ્યાઓ અને પૂર્ણ સંખ્યાઓ ઓળખી શકશો.',
    'Model whole numbers': 'પૂર્ણ સંખ્યાઓને નમૂના દ્વારા દર્શાવી શકશો.',
    'Identify the place value of a digit': 'અંકની સ્થાનકિંમત ઓળખી શકશો.',
    'Use place value to name whole numbers': 'સ્થાનકિંમતનો ઉપયોગ કરીને પૂર્ણ સંખ્યાઓ શબ્દોમાં કહી શકશો.',
    'Use place value to write whole numbers': 'સ્થાનકિંમતનો ઉપયોગ કરીને પૂર્ણ સંખ્યાઓ અંકોમાં લખી શકશો.',
    'Round whole numbers': 'પૂર્ણ સંખ્યાઓને નજીકની સ્થાનકિંમતમાં ફેરવી શકશો.',
    'coordinate': 'નિર્દેશાંક',
    'A number paired with a point on a number line is called the coordinate of the point.': 'સંખ્યારેખા પરના કોઈ બિંદુ સાથે જોડાયેલી સંખ્યાને તે બિંદુનો નિર્દેશાંક કહે છે.',
    'counting numbers': 'ગણતરીની સંખ્યાઓ',
    'The counting numbers are the numbers 1, 2, 3, ….': 'ગણતરીની સંખ્યાઓ એટલે 1, 2, 3, ….',
    'number line': 'સંખ્યારેખા',
    'A number line is used to visualize numbers. The numbers on the number line get larger as they go from left to right, and smaller as they go from right to left.': 'સંખ્યાઓને દૃશ્યરૂપે દર્શાવવા સંખ્યારેખાનો ઉપયોગ થાય છે. સંખ્યારેખા પર ડાબેથી જમણે જતાં સંખ્યાઓ મોટી થાય છે અને જમણેથી ડાબે જતાં નાની થાય છે.',
    'origin': 'ઉગમબિંદુ',
    'The origin is the point labeled 0 on a number line.': 'સંખ્યારેખા પર 0 લખેલા બિંદુને ઉગમબિંદુ કહે છે.',
    'place value system': 'સ્થાનકિંમત પદ્ધતિ',
    'Our number system is called a place value system because the value of a digit depends on its position, or place, in a number.': 'આપણી સંખ્યાપદ્ધતિને સ્થાનકિંમત પદ્ધતિ કહે છે, કારણ કે અંકનું મૂલ્ય સંખ્યામાં તે કયા સ્થાને છે તેના પર આધાર રાખે છે.',
    'rounding': 'નજીકની સ્થાનકિંમતમાં ફેરવવું (ગોળ કરવું)',
    'The process of approximating a number is called rounding.': 'સંખ્યાનું અંદાજિત મૂલ્ય મેળવવાની આ પ્રક્રિયાને નજીકની સ્થાનકિંમતમાં ફેરવવું, અથવા ગોળ કરવું, કહે છે.',
    'whole numbers': 'પૂર્ણ સંખ્યાઓ',
    'The whole numbers are the numbers 0, 1, 2, 3, ….': 'પૂર્ણ સંખ્યાઓ એટલે 0, 1, 2, 3, ….',
}


def normalize(text):
    return ' '.join(text.split())


def translate_fragment(source, mapping, metadata=False):
    result = deepcopy(source)
    translated = 0
    for el in result.iter():
        for field in ('text', 'tail'):
            value = getattr(el, field)
            if not value or not re.search('[A-Za-z]', value):
                continue
            if metadata and el.tag in (f'{{{MD}}}uuid', f'{{{MD}}}content-id'):
                continue
            key = normalize(value)
            if key not in mapping:
                raise ValueError(f'Untranslated {el.tag} {el.get("id")} {field}: {key}')
            # Preserve whitespace at node boundaries; translate the lexical slot.
            lead = re.match(r'^\s*', value).group()
            tail = re.search(r'\s*$', value).group()
            setattr(el, field, lead + mapping[key] + tail)
            translated += 1
        for field in ('alt', 'title'):
            if field in el.attrib:
                el.set(field, mapping[normalize(el.get(field))])
                translated += 1
    return result, translated


def validate_pair(source, translated):
    left, right = list(source.iter()), list(translated.iter())
    assert len(left) == len(right)
    for a, b in zip(left, right):
        assert a.tag == b.tag
        assert {k:v for k,v in a.attrib.items() if k not in ('alt','title')} == {k:v for k,v in b.attrib.items() if k not in ('alt','title')}
        assert len(a) == len(b)
        for field in ('text', 'tail'):
            x, y = getattr(a, field), getattr(b, field)
            # Every numerical token, including numbers outside MathML, survives.
            assert re.findall(r'\d+(?:[.,]\d+)*', x or '') == re.findall(r'\d+(?:[.,]\d+)*', y or ''), (a.tag,a.get('id'),field,x,y)
            if not re.search('[A-Za-z]', x or ''):
                assert x == y, (a.tag,a.get('id'),field,x,y)
        if a.tag.startswith(f'{{{M}}}') and a.tag != f'{{{M}}}mtext':
            assert a.text == b.text
    return {'elements': len(left), 'ids': sum('id' in x.attrib for x in left),
            'exercises': sum(x.tag == f'{{{C}}}exercise' for x in left),
            'source_solutions': sum(x.tag == f'{{{C}}}solution' for x in left),
            'math_expressions': sum(x.tag == f'{{{M}}}math' for x in left)}


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SHA
    source = ET.parse(SOURCE).getroot()
    original = source.find(f'.//{{{C}}}section[@id="fs-id2279009"]')
    translated, count = translate_fragment(original, TEXT)
    # Two source paragraphs share the English tail "in" but require different
    # Gujarati syntax. Use source identifiers to correct this exact occurrence.
    china = translated.find(f'.//{{{C}}}para[@id="fs-id4171773"]')
    china.find(f'{{{M}}}math').tail = ' હતી, વર્ષ '
    # Dates stay in the original source order with unchanged MathML punctuation.
    stats = validate_pair(original, translated)
    document = ET.Element(f'{{{C}}}document', {'{http://www.w3.org/XML/1998/namespace}lang':'gu-Gujr-IN'})
    ET.SubElement(document, f'{{{C}}}title').text = 'પૂર્ણ સંખ્યાઓનો પરિચય: વિભાગનો અભ્યાસ'
    ET.SubElement(document, f'{{{C}}}content').append(translated)
    ET.ElementTree(document).write(OUT/'a00-m81243-exercises.gu.cnxml', encoding='utf-8', xml_declaration=True)

    translated_metadata, metadata_count = translate_fragment(source.find(f'{{{C}}}metadata'), META, metadata=True)
    translated_glossary, glossary_count = translate_fragment(source.find(f'{{{C}}}glossary'), META)
    validate_pair(source.find(f'{{{C}}}metadata'), translated_metadata)
    validate_pair(source.find(f'{{{C}}}glossary'), translated_glossary)
    result = {
        'format': 'source-bound-cnxml-metadata-v1', 'locale': 'gu-Gujr-IN',
        'source_module': 'm81243', 'source_sha256': SHA,
        'document_title': META['Introduction to Whole Numbers'],
        'metadata_cnxml': ET.tostring(translated_metadata, encoding='unicode'),
        'glossary_cnxml': ET.tostring(translated_glossary, encoding='unicode'),
        'self_check_table': {
            'figure_id': 'eip-id1165721974706', 'media_id': 'eip-id1165721974707',
            'source_image': '../../media/CNX_BMath_Figure_AppB_001.jpg',
            'source_image_sha256': hashlib.sha256((ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/CNX_BMath_Figure_AppB_001.jpg').read_bytes()).hexdigest(),
            'headers': ['હું આ કરી શકું છું…', 'વિશ્વાસપૂર્વક', 'થોડી મદદથી', 'ના—મને સમજાતું નથી!'],
            'rows': [
                'ગણતરીની સંખ્યાઓ અને પૂર્ણ સંખ્યાઓ ઓળખી શકું છું.',
                'પૂર્ણ સંખ્યાઓને નમૂના દ્વારા દર્શાવી શકું છું.',
                'અંકની સ્થાનકિંમત ઓળખી શકું છું.',
                'સ્થાનકિંમતનો ઉપયોગ કરીને પૂર્ણ સંખ્યાઓ શબ્દોમાં કહી શકું છું.',
                'સ્થાનકિંમતનો ઉપયોગ કરીને પૂર્ણ સંખ્યાઓ અંકોમાં લખી શકું છું.',
                'પૂર્ણ સંખ્યાઓને નજીકની સ્થાનકિંમતમાં ફેરવી શકું છું.',
            ],
            'note': 'The complete source image was visually read. These six rows and four column headings translate its text. Keep all response cells empty; do not record pupil responses in this publication.',
        },
        'coverage': {**stats, 'translated_exercise_slots': count, 'translated_metadata_slots': metadata_count,
                     'translated_glossary_slots': glossary_count, 'glossary_definitions': 7, 'learning_objectives': 6},
        'limitations': [
            'Preserved source international grouping and international scale names; no silent conversion to lakh/crore.',
            'Historic estimates, years and units are source examples, not updated factual claims.',
            'Original self-check raster still contains English text; integrate the supplied Gujarati table into the reader.',
            'Native educator review remains pending, especially international number names and rounding terminology.',
        ],
    }
    (OUT/'a00-m81243-metadata.gu.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result['coverage'], ensure_ascii=False))


if __name__ == '__main__':
    main()
