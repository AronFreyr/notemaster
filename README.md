# Notemaster

The incredible notetaking wiki software that steals all
of the good ideas from Wikipedia
but with the added twist that
the entire structure of the application is tag based.


## TODO
Here is the incredibly unprofessional issue tracker!
### Backlog
* Easier way to add multiple tags to an existing document in the "edit-doc" view.
* Actually have some help text in the help section.
* Possibility to export documents to XML.
* Way to delete images.
* Look at this for ideas on the structure of the website, it might be useful: https://github.com/HassenPy/CRM-easy-app/blob/master/templates/base.html
* See if there is a better way to display links related to documents.
* Way to search for documents by tags with AND, OR, XOR etc.
* A better issue tracker, Trello looks promising.
* Useful and relevant information in this readme file.
* Think about scss integration.
* Possible "createaccount" functionality.
* Login and Logout pages that are not so barebones.
* Change the default admin password.
* Remote hosting (probably AWS).
* Mobile friendly version.
* Logging?
* More meta-tag variants
* Meta versions of documents? (Documents marked as operation notes, other as installation notes or something like that.)
* Document(article) of the day on homepage?
* Image of the day on homepage?
* time created and last edited fields for the Document, Tag, Image models?
* Possibly store edit history of documents.
* Change the admin password.
* Check out Django-Channels for asynchronous support.
    * https://github.com/django/channels
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
* Database that is not sqlite.
    * External database(maybe on AWS).
* Better portal ideas.
    * Check this out: https://en.wikipedia.org/wiki/Portal:Television_in_the_United_Kingdom
* Rename the Django project, notesfromxml is hardly applicable anymore.
    * new name ideas:
        * NoteTaker
        * Notus
        * NoteViewer
        * WikiWorld
        * ????
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
* Better bootstrap
    * Take a look at this https://getbootstrap.com/docs/4.1/getting-started/introduction/
* Reorganize the git branches.
* Remove all of the old XML test code from the project.
* Have specific pages for creating documents and images.
* Search bar in the header.
* Stuck Header navbar.
* Find a way to display XML code examples without the <> going crazy.
* Try out meta-tags for documents that should be displayed as a list.
* Safety prompt when using the delete or remove buttons.
    * DONE for deleting documents.
    * DONE for removing tags from documents.
    * DONE for deleting tags.
    * DONE for removing documents from tags.
* Password protection.