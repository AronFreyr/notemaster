from io import StringIO, BytesIO
import lxml.html
from lxml import etree


def not_test_function():
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

    #doc = etree.fromstring(test_text)
    #for x in doc.itertext():
    #    print(x.strip())
    # print(doc)

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(test_text), parser)
    result = etree.tostring(tree.getroot(), pretty_print=True, method='html')
    #print(result)

    html = etree.HTML(test_text)
    result = etree.tostring(html, pretty_print=True, method='html')
    print('result: ', result)

    result = lxml.html.parse(test_text)
    print('result:', result)


if __name__ == '__main__':
    not_test_function()
