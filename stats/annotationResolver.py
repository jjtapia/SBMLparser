
import bioservices
import pyparsing as pyp
goGrammar = pyp.Suppress(pyp.Literal('<name>')) +  pyp.Word(pyp.alphanums + ' -_') + pyp.Suppress(pyp.Literal('</name>')) 

def resolveAnnotation(annotation):
    if not hasattr(resolveAnnotation, 'db'):
        resolveAnnotation.db = {}
        resolveAnnotation.ch = bioservices.ChEBI(verbose=False)
        resolveAnnotation.uni = bioservices.UniProt(verbose=False)
        resolveAnnotation.k = bioservices.kegg.KEGGParser(verbose=False)
        resolveAnnotation.qg = bioservices.QuickGO(verbose=False)
        resolveAnnotation.db['http://identifiers.org/uniprot/P62988'] = 'http://identifiers.org/uniprot/P62988'
        resolveAnnotation.db['http://identifiers.org/uniprot/P06842'] = 'http://identifiers.org/uniprot/P06842'
        resolveAnnotation.db['http://identifiers.org/uniprot/P07006'] = 'http://identifiers.org/uniprot/P06842'
        
    if annotation in resolveAnnotation.db:
        return annotation,resolveAnnotation.db[annotation]
    
        
    tAnnotation = annotation.replace('%3A',':')
    tAnnotation = annotation.split('/')[-1]
    #tAnnotation = re.search(':([^:]+:[^:]+$)',tAnnotation).group(1)
    try:
        if 'obo.go' in annotation or '/go/GO' in annotation:

            res = resolveAnnotation.qg.Term(tAnnotation)
            res = bioservices.Service('name').easyXML(res)            
            tmp = res.findAll('name')
            finalArray = []
            for x in tmp:
                try:
                    tagString = str(goGrammar.parseString(str(x))[0])
                    if tagString not in ['Systematic synonym']:
                        finalArray.append(str(goGrammar.parseString(str(x))[0]))
                except pyp.ParseBaseException:
                    continue
                
            resolveAnnotation.db[annotation] = finalArray[0]
            finalAnnotation =  resolveAnnotation.db[annotation]
    
        elif 'kegg' in annotation:
            
            data = resolveAnnotation.k.get(tAnnotation)
            dict_data =  resolveAnnotation.k.parse(data)
            resolveAnnotation.db[annotation] = dict_data['name']
            finalAnnotation = resolveAnnotation.db[annotation]
            
        elif 'uniprot' in annotation:
            identifier = annotation.split('/')[-1]
            result = resolveAnnotation.uni.quick_search(identifier)
            if identifier in result:
                resolveAnnotation.db[annotation] = result[identifier]['Protein names'].split('(')[0]
            else:
                finalAnnotation = ''
            finalAnnotation = resolveAnnotation.db[annotation]
            
        elif 'chebi' in annotation:
            tmp = annotation.split('/')[-1]
            
            entry = resolveAnnotation.ch.getLiteEntity(tmp)
            finalAnnotation = ''
            for element in entry:
                resolveAnnotation.db[annotation] = str(element['chebiAsciiName'])
                finalAnnotation = resolveAnnotation.db[annotation]
        elif 'cco' in annotation or 'pirsf' in annotation or 'pubchem' in annotation or 'omim' in annotation:
            finalAnnotation = ''
        #elif 'taxonomy' in annotation:
            #uniprot stuff for taxonomy
        #    pass
            '''
            url = 'http://www.uniprot.org/taxonomy/'
            params = {
            'from':'ACC',
            'to':'P_REFSEQ_AC',
            'format':'tab',
            'query':'P13368 P20806 Q9UM73 P97793 Q17192'
            }
            
            data = urllib.urlencode(params)
            request = urllib2.Request(url, data)
            contact = "" # Please set your email address here to help us debug in case of problems.
            request.add_header('User-Agent', 'Python contact')
            response = urllib2.urlopen(request)
            page = response.read(200000)
            '''
        else:
            return annotation,''
            #assert(False)
            finalAnnotation = ''
    except (IOError,KeyError) as e:
        return annotation,''
    return annotation,finalAnnotation

if __name__ == "__main__":
    print resolveAnnotation('http://identifiers.org/go/GO:0030119')
    #print resolveAnnotation('http://identifiers.org/uniprot/P01133')