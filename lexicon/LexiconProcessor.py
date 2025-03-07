from tokenization import Tokenization
import unicodedata

class LexiconProcessor:
        
    def __init__(self,lexicon):
        self.lexicon = lexicon
    
    def add_data(self,data,feats,col_token=1,col_lemma=2,col_upos=3,col_xpos=4,col_morph=5,normalization_rule=None):
        for sent in data:
            for line in sent.split("\n"):
                split = line.split("\t")
                morph = split[col_morph]
                morph_dict = {}
                if morph != '_':
                    for feat_val in morph.split('|'):
                        feat, val = feat_val.split('=')
                        morph_dict[feat] = val
                tag = []
                for feat in feats:
                    if feat == 'UPOS':
                        tag.append((feat, split[col_upos]))
                    elif feat == 'XPOS':
                        tag.append((feat, split[col_xpos]))
                    elif feat == 'lemma':
                        tag.append((feat, split[col_lemma]))
                    else:
                        if feat in morph_dict:
                            tag.append((feat, morph_dict[feat]))
                        else:
                            tag.append((feat, '_'))
                tag = tuple(tag)
                form = split[col_token]
                if normalization_rule == 'greek_glaux':
                    form = Tokenization.normalize_greek_punctuation(form)
                    form = Tokenization.normalize_greek_nfd(form)
                    form = Tokenization.normalize_greek_accents(form)
                elif normalization_rule == 'NFD' or normalization_rule == 'NFKD' or normalization_rule == 'NFC' or normalization_rule == 'NFKC':
                    form = unicodedata.normalize(normalization_rule,form)
                if form in self.lexicon:
                    tags = self.lexicon[form]
                    if tag not in tags:
                        tags.append(tag)
                else:
                    tags = []
                    tags.append(tag)
                    self.lexicon[form] = tags
    
    def write_lexicon(self,output,morph_feats,output_format='tab',lemma_name='lemma',pos_name='XPOS'):
        entries_processed = set()
        with open(output, 'w', encoding='UTF-8') as outfile:
            if output_format=='tab':
                outfile.write('form\tlemma\tXPOS')
                for feat in morph_feats:
                    outfile.write('\t'+feat)
                outfile.write('\n')
            for form, entry in self.lexicon.items():
                for analysis in entry:
                    analysis_dict = dict(analysis)
                    if output_format=='CONLL':
                        morph = ''
                        for feat in morph_feats:
                            val = analysis_dict[feat]
                            if val != '_':
                                morph += feat + '=' + val + '|'
                        if len(morph) == 0:
                            morph = '_'
                        else:
                            morph = morph.rstrip(morph[-1])
                        line = form+'\t'+analysis_dict[lemma_name]+'\t'+analysis_dict[pos_name]+'\t'+morph+'\n'
                        if not line in entries_processed:
                            outfile.write(line)
                        entries_processed.add(line)
                    elif output_format=='tab':
                        line = form+'\t'+analysis_dict[lemma_name]+'\t'+analysis_dict[pos_name]
                        for feat in morph_feats:
                            line += '\t'+analysis_dict[feat]
                        line+='\n'
                        if not line in entries_processed:
                            outfile.write(line)
                        entries_processed.add(line)
                        