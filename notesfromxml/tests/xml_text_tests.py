from django.test.testcases import TestCase
from notesfromxml.models import Document, Tag, Tagmap


class XMLTextTests(TestCase):

    def test_parse_xml_text(self):
        html_text = """
        <p>Lets Spring auto-wire other beans into your classes using <code>@Autowired</code> annotation. 
        Spring beans can be wired by name or by type.</p> 
        <ul>
        <li>
        <code>@Autowire</code> by default is a type driven injection. <code>@Qualifier</code> spring annotation can be used to further fine-tune autowiring.
        </li>
        <li>
        <code>@Resource</code> (javax.annotation.Resource) annotation can be used for wiring by name.
        </li>
        <p>Beans that are themselves defined as a collection or map type cannot be injected through @Autowired, because type matching is not properly applicable to them.
        Use @Resource for such beans, referring to the specific collection or map bean by unique name.  @Autowired allows you to do a single:</p>
        <pre><code class="language-java" data-lang="java">@Autowired
        public NBIServiceImpl nbiServicePort;</code></pre>
        
        <p>Instead of constantly doing:</p>
        
        <pre><code class="language-java" data-lang="java">
        NBIServiceImpl nbiServiceImpl = new NBIServiceImpl(nbiServicePort, env);
        </code></pre>
        
        <p>Whenever you want to make a new NBIServiceImpl object.
        For this to work, the NBIServiceImpl class must have a constructor like so:</p>
        <pre><code class="language-java" data-lang="java">@Inject     public NBIServiceImpl(NBIServicePort client, Environment env) {         this.client = client;         this.env = env;     }</code></pre>
        
        <p>Why @Inject? I don't know. Some say that there is no difference between @Autowired and @Inject but that has yet to be confirmed.</p>
        """


