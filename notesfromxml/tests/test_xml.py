from django.test.testcases import TestCase
from collections import defaultdict
from lxml import etree
import os


class RecursiveXMLTests(TestCase):

    def test_recursive(self):

        def get_xml_file():
            module_dir = os.path.dirname(__file__)  # Gets the current path.
            file_path = os.path.join(module_dir, 'general.xml')  # This is so we can open general.xml in the current path.
            data = etree.parse(file_path)  # Creates a tree structure from general.xml.
            root_dict = etree_to_dict(data.getroot())  # Converts the tree structure into a dictionary.
            return root_dict

        def etree_to_dict(t):
            d = {t.tag: {} if t.attrib else None}
            children = list(t)
            if children:
                dd = defaultdict(list)
                for dc in map(etree_to_dict, children):
                    for k, v in dc.items():
                        dd[k].append(v)
                d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
            if t.attrib:
                d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
            if t.text:
                text = t.text.strip()
                if children or t.attrib:
                    if text:
                        d[t.tag]['#text'] = text
                else:
                    d[t.tag] = text
            return d

        def dict_recursion(input_dict):
            if type(input_dict) is dict:
                #print('input_dict is a dictionary:')
                #print(input_dict.keys())
                for dict_item in input_dict.items():
                    #print('dict item[0]', dict_item[0])
                    dict_recursion(dict_item[1])
            elif type(input_dict) is list:
                #print('input_dict is a list:')
                for x in input_dict:
                    #print('list item:')
                    #print(x)
                    dict_recursion(x)
            #else:
                #print('input_dict is not a dictionary:')
                #print(input_dict)

        xml_dict = get_xml_file()
        dict_recursion(xml_dict)
        html_string = ''

        def dict_recursion_with_html(input_dict, html_string_input):
            if input_dict is None:
                print('input_dict is None')
                return
            print('input_dict', input_dict)
            if type(input_dict) is dict:
                print('input_dict is a dictionary:')
                #print(input_dict.keys())
                for dict_item in input_dict.items():
                    print('<div>')
                    html_string_input += '<h2>' + dict_item[0] + '</h2>'
                    print('dict item[0]', '<h2>' + dict_item[0] + '</h2>')
                    dict_recursion_with_html(dict_item[1], html_string_input)
                    print('</div>')
            elif type(input_dict) is list:
                print('input_dict is a list:')
                for x in input_dict:
                    #print('list item:')
                    #print(x)
                    dict_recursion_with_html(x, html_string_input)
            else:
                #print('input_dict is not a dictionary:')
                print('<p>' + input_dict + '</p>')
                html_string_input += '<p>' + input_dict + '</p>'
            print('html_string_input: ', html_string_input)
            print('END!!!')

        dict_recursion_with_html(xml_dict, html_string)
         #return_html = dict_recursion_with_html(xml_dict, html_string)


class ParsingXMLTests(TestCase):

    def test_xml_tag_in_text(self):
        test_text = '''
            <p>
            Lets Spring auto-wire other beans into your classes using @Autowired annotation. 
            Spring beans can be wired by name or by type. 
            1) @Autowire by default is a type driven injection. @Qualifier spring annotation can be used to further fine-tune autowiring.
            2) @Resource (javax.annotation.Resource) annotation can be used for wiring by name.
            Beans that are themselves defined as a collection or map type cannot be injected through @Autowired, because type matching is not properly applicable to them.
            Use @Resource for such beans, referring to the specific collection or map bean by unique name.  @Autowired allows you to do a single:
            <pre><code class="language-java" data-lang="java">@Autowired
            public NBIServiceImpl nbiServicePort;</code></pre>
            Instead of constantly doing:
            
            NBIServiceImpl nbiServiceImpl = new NBIServiceImpl(nbiServicePort, env);
            
            Whenever you want to make a new NBIServiceImpl object.
            For this to work, the NBIServiceImpl class must have a constructor like so:
            
            @Inject     public NBIServiceImpl(NBIServicePort client, Environment env) {         this.client = client;         this.env = env;     }
            
            Why @Inject? I don't know. Some say that there is no difference between @Autowired and @Inject but that has yet to be confirmed.
            </p>
        '''
        doc = etree.parse(test_text)
        print(doc)


class ThisIsNotATest:

    def not_test_function(self):
        test_text = '''
                    <p>
                    Lets Spring auto-wire other beans into your classes using @Autowired annotation. 
                    Spring beans can be wired by name or by type. 
                    1) @Autowire by default is a type driven injection. @Qualifier spring annotation can be used to further fine-tune autowiring.
                    2) @Resource (javax.annotation.Resource) annotation can be used for wiring by name.
                    Beans that are themselves defined as a collection or map type cannot be injected through @Autowired, because type matching is not properly applicable to them.
                    Use @Resource for such beans, referring to the specific collection or map bean by unique name.  @Autowired allows you to do a single:
                    <pre><code class="language-java" data-lang="java">@Autowired
                    public NBIServiceImpl nbiServicePort;</code></pre>
                    Instead of constantly doing:

                    NBIServiceImpl nbiServiceImpl = new NBIServiceImpl(nbiServicePort, env);

                    Whenever you want to make a new NBIServiceImpl object.
                    For this to work, the NBIServiceImpl class must have a constructor like so:

                    @Inject     public NBIServiceImpl(NBIServicePort client, Environment env) {         this.client = client;         this.env = env;     }

                    Why @Inject? I don't know. Some say that there is no difference between @Autowired and @Inject but that has yet to be confirmed.
                    </p>
                '''
        doc = etree.parse(test_text)
        print(doc)