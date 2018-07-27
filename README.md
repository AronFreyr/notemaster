# Notemaster

The incredible notetaking wiki software that steals all
of the good ideas from Wikipedia
but with the added twist that
the entire structure of the application is tag based.


## TODO
Here is the incredibly unprofessional issue tracker!
### Backlog
* Search bar in the header.
* Safety prompt when using the delete or remove buttons.
* Better bootstrap
    * Take a look at this https://getbootstrap.com/docs/4.1/getting-started/introduction/
* Actually have some help text in the help section.
* Possibility to export documents to XML.
* Way to delete images.
* Database that is not sqlite.
    * External database(maybe on AWS).
* Look at this for ideas on the structure of the website, it might be useful: https://github.com/HassenPy/CRM-easy-app/blob/master/templates/base.html
* Password protection.
* Better portal ideas.
* Find a way to display XML code examples without the <> going crazy.
* See if there is a better way to display links related to documents.
* Way to search for documents by tags with AND, OR, XOR etc.
### In Progress
* Possibility to display bold, italic and such text in the documents.
* Easier image display.
* Need to find a better way to display html tags in text.
    * Check this out!: https://stackoverflow.com/questions/14007033/django-storing-website-content
    * And this: https://docs.djangoproject.com/en/2.0/ref/contrib/flatpages/
    * https://stackoverflow.com/questions/18539440/extract-tag-inside-text-element-of-an-xml-tag
* Improve the text parser for text in documents.
    * See examples on how Wikipedia does it: https://web.archive.org/web/20110709125138/http://musialek.org/?p=94
    * Another example: https://www.mediawiki.org/wiki/Manual:Parser.php
### Done
* Possibility for adding multiple tags at a time to a document.
* Help site for the wiki (preferably as a link in the header bar)
* Create a parser that can hyperlink from text to documents.
    * Allow the parser to insert html code tags to make Java code pretty.
    * Let the parser control whether images are to the left or right in text.
* Possibility to display code in a special block that is not ugly in documents.
* Image integration
* Prototype for portals.
* Have a convenient way to display links to other pages.