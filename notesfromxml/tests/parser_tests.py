from django.test.testcases import TestCase
from notesfromxml.models import Document, Tag, Tagmap
from notesfromxml.services.parser import tagged_docs_to_list_parser
import re


class TaggedDocsToListTests(TestCase):

    def test_doc_to_list_function(self):
        Document.objects.create(document_name="Java", document_text="Java document text test 1")
        Document.objects.create(document_name="JAXB", document_text="JAXB document text test 1")
        Document.objects.create(document_name="XML", document_text="XML document text test 1")

        Tag.objects.create(tag_name="Java")
        Tag.objects.create(tag_name="JAXB")
        Tag.objects.create(tag_name="XML")

        Tagmap.objects.create(document=Document.objects.get(document_name="Java"), tag=Tag.objects.get(tag_name="Java"))
        Tagmap.objects.create(document=Document.objects.get(document_name="JAXB"), tag=Tag.objects.get(tag_name="Java"))
        Tagmap.objects.create(document=Document.objects.get(document_name="JAXB"), tag=Tag.objects.get(tag_name="JAXB"))
        Tagmap.objects.create(document=Document.objects.get(document_name="JAXB"), tag=Tag.objects.get(tag_name="XML"))
        Tagmap.objects.create(document=Document.objects.get(document_name="XML"), tag=Tag.objects.get(tag_name="XML"))

        text_to_parse = 'lorem ipsum [list[[Java]]] ipsum lorem.'
        tagged_docs_to_list_parser(text_to_parse)

    def test_get_type_of_match_and_text_of_match(self):
        text = """<p><code>@Autowired</code> is a [[[Spring Annotations| Spring annotation]]] that allows [[[Spring]]] to auto-wire other beans into your classes. 
Spring beans can be wired by name or by type.</p>
<ul>
<li>
<code>@Autowired</code> by default is a type driven injection. <code>[[[@Qualifier (Spring Annotation) | @Qualifier]]]</code> spring annotation can be used to further fine-tune autowiring.
</li>
<li>
<code>@Resource</code>(javax.annotation.Resource) annotation can be used for wiring by name.
</li>
</ul>
[image[[Spring Logo | side=right]]]
<p>Beans that are themselves defined as a collection or map type cannot be injected through <code>@Autowired</code>, because type matching is not properly applicable to them.
Use <code>@Resource</code> for such beans, referring to the specific collection or map bean by unique name.</p>
<p><code>@Autowired</code> allows you to do a single:</p>
[java[[
@Autowired
public NBIServiceImpl nbiServicePort;
]]]
<p>Instead of constantly doing:</p>

[java[[
NBIServiceImpl nbiServiceImpl = new NBIServiceImpl(nbiServicePort, env); [test[[testtext [test2[[testext222222]]]222222 ]]] somethin something textysomething
]]]

<p>Whenever you want to make a new NBIServiceImpl object.</p>
<p>For this to work, the NBIServiceImpl class must have a constructor like so:</p>

[java[[
@Inject
public NBIServiceImpl(NBIServicePort client, Environment env) {
     this.client = client;
     this.env = env;
}
]]]

<p>Why <code>@Inject</code>? I don't know. Some say that there is no difference between <code>@Autowired</code> and <code>@Inject</code> but that has yet to be confirmed.</p>

[links[[
A Stack Overflow question and answer on the appropriate usage of the @Autowired annotation | http://stackoverflow.com/questions/19414734/understanding-spring-autowired-usage ;
A good Stack Overflow question and answer on what is going wrong when the autowired dependencies register as null | http://stackoverflow.com/questions/19896870/why-is-my-spring-autowired-field-null?rq=1]]]"""
        #pattern = re.compile(r'\[(.*?)\[\[(.*?)\]\]\]', re.DOTALL)

        parsed_text = text
        # This goes through the text again and again from the beginning until it finds no matches
        while self.is_match(parsed_text):
            parsed_text = self.find_match(parsed_text)
        print('------------PARSED TEXT------------')
        print(parsed_text)

    def find_match(self, input_text):
        pattern = re.compile(r'\[(.*?)\[\[(.*?)\]\]\]', re.DOTALL)
        matches = re.finditer(pattern, input_text)
        if matches is not None:  # If match is found.
            for match in matches:
                entire_match = match.group()
                matched_type = match.group(1)
                matched_text = match.group(2)
                string_to_cut = '[' + matched_type + '[['  # Cut the [[[ in front but not the ]]] in back
                cut_string = entire_match[len(string_to_cut):]

                if self.is_match(cut_string):  # If a match is found inside the match.
                    new_matched_text = self.find_match(cut_string)  # Recurse
                    print('matched_text: ' + matched_text)
                    # Replace the text plus ]]] and return it so the match inside the match is properly parsed.
                    input_text = input_text.replace(matched_text + ']]]', new_matched_text)
                    return input_text

                new_text = '<' + matched_type + '>' + matched_text + '</' + matched_type + '>'
                input_text = input_text.replace(entire_match, new_text)
                return input_text

        return input_text

    def is_match(self, input_text):
        pattern = re.compile(r'\[(.*?)\[\[(.*?)\]\]\]', re.DOTALL)
        matches = re.finditer(pattern, input_text)
        # Returns true if there is any element in the iterator without removing the element.
        return any(True for _ in matches)

