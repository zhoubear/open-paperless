2.7.3 (2017-09-11)
==================
- Fix task manager queue list view. Thanks to LeVon Smoker for
  the report.
- Fix resolved link class URL mangling when the keep_query argument is
  used. Thanks to Nick Douma (LordGaav) for the report and diagnostic
  information. Fixes source navigation on the document upload wizard.

2.7.2 (2017-09-06)
==================
- Fix new mailer creation view. GitLab issue #431.
  Thanks to Robert Schöftner (@robert.schoeftner) for the
  report and the solution.
- Consolidate intial document created event and the first
  document properties edited events. Preserve the user that
  initially creates the document. GitLab issue #433. Thanks
  to Jesaja Everling (@jeverling) for the report.
- Sort the list of root cabinets. Thanks to Thomas Plotkowiak
  for the request.
- Sort the list of a document's cabinets.
- Display a document's cabinet list in italics. GitLab issue #435.
  Thanks to LeVon Smoker for the request.
- Install mock by default to allow easier testing of deployed
  instances.

2.7.1 (2017-09-03)
==================
- Support unicode in URL querystring. GitLab issue #423.
  Thanks to Gustavo Teixeira (@gsteixei) for the find.
- Import errors during initialization are only ignored
  if they are cause by a missing local.py. Thanks to
  MacRobb Simpson for the report and solution.
- Make sure the local.py created used unicode for strings
  by default. GitLab issue #424. Thanks to Gustavo Teixeira
  (@gsteixei) for the find.

2.7 (2017-08-30)
================
- Add workaround for PDF with IndirectObject as the
  rotation value. GitHub #261.
- Add ACL list link with icon and use it for the document facet menu.
- Fix mailing app permissions labels.
- Add ACLs link and ACLs permissions to the mailer profile model.
- Improve mailer URL regex.
- Add ordering support to the SourceColumn class. GitLab issue #417.
- Shows the cabinets in the document list. GitLab #417 @corneliusludmann
- Add workaround for pycountry versions without the bibliographical key.
  GitHub issue #250.
- Skip UUID migration on Oracle backends. GitHub issue #251.
- Allow changing the output format, DPI of the pdftoppm command, and
  the output format of the converter via the CONVERTER_GRAPHICS_BACKEND_CONFIG
  setting. GitHub issues #256 #257 GitLab issue #416.
- Add support for workflow triggers.
- Add support for workflow actions.
- Add support for rendering workflows.
- Add support for unbinding sub menus.
- Fix mailing profile test view.
- Disregard the last 3 dots that mark the end of the YAML document.
- Add support for multiple dashboards.
- Add support for removing dashboard widgets.
- Convert document version view to item list view.
- Add support for browsing individual document versions.
- Add support for dropdown menus to the item list view template.
- Add support for preserving the file extenstion when downloading a document
  version. GitLab #415.
- Split OCR app into OCR and parsing.
- Remove Folders app.
- Use the literal 'System' instead of the target name when
  the action user in unknown.
- Remove the view to submit all document for OCR.
- When changing document types, don't delete the old metadata that is
  also found in the new document type. GitLab issue #421.
- Add tag attach and tag remove events.
- Change the permission needed to attach and remove tags.
- Add HTTP POST workflow state action.
- Add access control grant workflow state action.
- Beta Python 3 support.

2.6.4 (2017-07-26)
==================
- Add missing replacements of reverse to resolve_url.

2.6.3 (2017-07-25)
==================
- Add makefile target to launch a PostgreSQL container.
- Use resolve_url instead of redirect to resolve the post login URL.
- Make the intialsetup and performupgrade management tasks work
  with signals to allow customization from 3rd party apps.
- PEP8 cleanups.
- Add tag_ids keyword argument to the Source.handle_upload
  model method. GitLab issue #413.
- Add overflow wrapping so wrap long titles in Firefox too.
- Makes Roles searchable. GitLab issue #402.
- Add line numbers to the debug and production loggers.
  Add date and time to the production logger.
- Add support for generating setup.py from a template. GitLab
  #149 #200.
- Add fade in animation to document images.

2.6.2 (2017-07-19)
==================
- Fix deprecation warning to prepare upgrade to Django 1.11 and 2.0.
- Fix document page zoom.
- Add support to run tests against a MySQL, Postgres or Oracle container.
- Improve tag widget customization by moving the markup to its own template.
- Fix document page widget appearance in the document page list view.
- Make document version order deterministic.
- Allow total page number instrospection of encrypted PDF with non ASCII user properties. GitLab issue #411.
- Oracle database compatibility update in the cabinets app. GitHub #258.

2.6.1 (2017-07-18)
==================
- Fix issue when editing or removing metadata from multiple documents.

2.6 (2017-07-18)
================
- Fix HTML mark up in window title. GitLab #397.
- Add support for emailing documents to a recipient list. GitLab #396.
- Backport metadata widget changes from @Macrobb. GitLab #377.
- Make users and group searchable.
- Add support for logging errors during in production mode.
  Add COMMON_PRODUCTION_ERROR_LOG_PATH to control path of log file.
  Defaults to mayan/error.log.
- Add support logging request exceptions.
- Add document list item view.
- Sort setting by namespace label and by global name second.
- Sort indexes by label.
- Fix cabinets permission and access control checking.
- The permission to add or remove documents to cabinets now applies to documents too.
- Equalize dashboard widgets heights.
- Switch the order of the DEFAULT_AUTHENTICATION_CLASSES of DRF. GitLab #400.
- Backport document's version list view permission.
- Improve code to unbind menu entries.
- Renamed the document type permission namespace from "Document setup" to "Document types".
- Add support for granting the document type edit, document type delete, and document type view
  permissions to individual document type instances.
- Improved tests by testing for accesses.
- Increase the size of the mailing profile label field to 128 characters.

2.5.2 (2017-07-08)
==================
- Improve new document creation signal handling.
  Fixes issue with duplicate scanning at upload.

2.5.1 (2017-07-08)
==================
- Update release target due to changes in PyPI.

2.5 (2017-07-07)
================
- Add view to download a document's OCR text. GitLab #215
- Add user configurable mailer. GitLab #286.
- Use Toasts library for screen messages.
- Reduce verbosity of some debug messages.
- Add new lineart transformation.
- Fix SANE source resolution field.
- About and Profile menu reorganization.
- PDF compatibility improvements.
- Office document coversion improvements.
- New metadata type setup UI.
- Duplicated document scan support.
- "Remember me" login support.
- Forgotten password restore via email.
- Document cache disabling.
- Translation improvements.
- Image loading improvements.
- Lower Javascript memory utilization.
- HTML reponsive layout improvements.
- Make document deletion a background task.
- Unicode handling improvements.
- Python3 compatilibyt improvements.
- New screen messages using Toastr.

2.4 (2017-06-23)
================
- Add Django-mathfilters.
- Improve render of documents with no pages.
- Add SANE scanner document source.
- Added PDF orientation detection. GitLab issue #387.
- Fix repeated permission list API URL. GitLab issue #389.
- Fix role creation API endpoint not returning id. GitLab issue #390.
- Make tags, metadata types and cabinets searchable via the dynamic search API. GitLab issue #344.
- Add support for updating configuration options from environment variables.
- Add purgelocks management command. GitLab issue #221.
- Fix index rebuilding for multi value first levels. GitLab issue #391.
- Truncate views titles via the APPEARANCE_MAXIMUM_TITLE_LENGTH setting. GitLab issue #217.
- Add background task manager app. GitLab issue #132.
- Add link to show a document's OCR errors. GitLab issue #291.

2.3 (2017-06-08)
================
- Allow for bigger indexing expression templates.
- Auto select checkbox when updating metadata values. GitLab issue #371.
- Added support for passing the options allow-other and allow-root to the
  FUSE index mirror. GitLab issue #385
- Add support for check for the latest released version of Mayan from the
  About menu.
- Support for rebuilding specific indexes. GitLab issue #372.
- Rewrite document indexing code to be faster and use less locking.
- Use a predefined file path for the file lock.
- Catch documents with not document version when displaying their thumbnails.
- Document page navigation fix when using Mayan as a sub URL app.
- Add support for indexing on workflow state changes.
- Add search model list API endpoint.

2.2 (2017-04-26)
================
- Remove the installation app (GitLab #301).
- Add support for document page search
- Remove recent searches feature
- Remove dependency on the django-filetransfer library
- Fix height calculation in resize transformation
- Improve upgrade instructions
- New image caching pipeline
- New drop down menus for the documents, folders and tags app as well as for
  the user links.
- New Dashboard view
- Moved licenses to their own module in every app
- Update project to work with Django 1.10.4.
- Tags are alphabetically ordered by label (GitLab #342).
- Stop loading theme fonts from the web (GitLab #343).
- Add support for attaching multiple tags (GitLab #307).
- Integrate the Cabinets app.

2.1.11 (2017-03-14)
===================
- Added a quick rename serializer to the document type API serializer.
- Added per document type, workflow list API view.
- Mayan EDMS was adopted a version 1.1 of the Linux Foundation Developer Certificate of Origin.
- Added the detail url of a permission in the permission serializer.
- Added endpoints for the ACL app API.
- Implemented document workflows transition ACLs. GitLab issue #321.
- Add document comments API endpoints. GitHub issue #249.
- Add support for overriding the Celery class.
- Changed the document upload view in source app to not use the HTTP referer
  URL blindly, but instead recompose the URL using known view name. Needed
  when integrating Mayan EDMS into other app via using iframes.
- Addes size field to the document version serializer.
- Removed the serializer from the deleted document restore API endpoint.
- Added support for adding or editing document types to smart links via the
  API.

2.1.10 (2017-02-13)
===================
- Update Makefile to use twine for releases.
- Add Makefile target to make test releases.

2.1.9 (2017-02-13)
==================
- Update make file to Workaround long standing pypa wheel bug #99

2.1.8 (2017-02-12)
==================
- Fixes in the trashed document API endpoints.
- Improved tags API PUT and PATCH endpoints.
- Bulk document adding when creating and editing tags.
- The version of django-mptt is preserved in case mayan-cabinets is installed.
- Add Django GPG API endpoints for singing keys.
- Add API endpoints for the document states (workflows) app.
- Add API endpoints for the messsage of the day (MOTD) app.
- Add Smart link API endpoints.
- Add writable versions of the Document and Document Type serializers (GitLab issues #348 and #349).
- Close GitLab issue #310 "Metadata's lookup with chinese messages when new document"

2.1.7 (2017-02-01)
==================
- Improved user management API endpoints.
- Improved permissions API endpoints.
- Improvements in the API tests of a few apps.
- Addition Content type list API view to the common app.
- Add API endpoints to the events app.
- Enable the parser and validation fields of the metadata serializer.

2.1.6 (2016-11-23)
==================
- Fix variable name typo in the rotation transformation class.
- Update translations

2.1.5 (2016-11-08)
==================
- Backport resize transformation math operation fix (GitLab #319).
- Update Pillow to 3.1.2 (Security fix).
- Backport zoom transformation performance improvement (GitLab #334).
- Backport trash can navigation link resolution fix (GitLab #331).
- Improve documentation regarding the use of GPG version 1 (GitLab #333).
- Fix ACL create view HTML response type. (GitLab #335).
- Expland staging folder and watch folder explanation.

2.1.4 (2016-10-28)
==================
- Add missing link to the 2.1.3 release notes in the index file.
- Improve TempfileCheckMixin.
- Fix statistics namespace list display view.
- Fix events list display view.
- Update required Django version to 1.8.15.
- Update required python-gnupg version to 0.3.9.
- Improved orphaned temporary files test mixin.
- Re-enable and improve GitLab CI MySQL testing.
- Improved GPG handling.
- New GPG backend system.
- Minor documentation updates.

2.1.3 (2016-06-29)
==================
- Add help message when initialsetup migration phase fails. Relates to GitLab issue #296.
- Start using self.setdout instead of print as per documentation.
- Fix GitLab issue #295, "When editing a user the top bar jumps to the name of the user".
- Normalize handling of temporary file and directory creation.
- Fix GitLab issue #309, "Temp files quickly filling-up my /tmp (1GB tmpfs)".
- Explicitly check for residual temporary files in tests.
- Add missing temporary file cleanup for office documents.
- Fix file descriptor leak in the document signature download test.

2.1.2 (2016-05-20)
==================
- Sort document languages and user profile locale language lists. GitLab issue #292.
- Fix metadata lookup for {{ users }} and {{ group }}. Fixes GitLab #290.
- Add Makefile for common development tasks

2.1.1 (2016-05-17)
==================
- Fix navigation issue that make it impossible to add new sources. GitLab issue #288.
- The Tesseract OCR backend now reports if the requested language file is missing. GitLab issue #289.
- Ensure the automatic default index is created after the default document type.

2.1 (2016-05-14)
================
- Upgrade to use Django 1.8.13. Issue #246.
- Upgrade requirements.
- Remove remaining references to Django's User model. GitLab issue #225
- Rename 'Content' search box to 'OCR'.
- Remove included login required middleware using django-stronghold instead (http://mikegrouchy.com/django-stronghold/).
- Improve generation of success and error messages for class based views.
- Remove ownership concept from folders.
- Replace strip_spaces middleware with the spaceless template tag. GitLab issue #255
- Deselect the update checkbox for optional metadata by default.
- Silence all Django 1.8 model import warnings.
- Implement per document type document creation permission. Closes GitLab issue #232.
- Add icons to the document face menu links.
- Increase icon to text spacing to 3px.
- Make document type delete time period optional.
- Fixed date locale handling in document properties, checkout and user detail views.
- Add new permission: checkout details view.
- Add HTML5 upload widget. Issue #162.
- Add Message of the Day app. Issue #222
- Update Document model's uuid field to use Django's native UUIDField class.
- Add new split view index navigation
- Newly uploaded documents appear in the Recent document list of the user.
- Document indexes now have ACL support.
- Remove the document index setup permission.
- Status messages now display the object class on which they operate not just the word "Object".
- More tests added.
- Handle unicode filenames in staging folders.
- Add staging file deletion permission.
- New document_signature_view permission.
- Add support for signing documents.
- Instead of multiple keyservers only one keyserver is now supported.
- Replace document type selection widget with an opened selection list.
- Add mailing documentation chapter.
- Add roadmap documentation chapter.
- API updates.


2.0.2 (2016-02-09)
==================
- Install testing dependencies when installing development dependencies.
- Fix GitLab issue #250 "Empty optional lookup metadata trigger validation error".
- Fix OCR API test.
- Move metadata form value validation to .clean() method.
- Only extract validation error messages from ValidationError exception instances.
- Don't store empty metadata value if the update checkbox is not checked.
- Add 2 second delay to document version tests to workaround MySQL limitation.
- Strip HTML tags from the browser title.
- Remove Docker and Docker Compose files.


2.0.1 (2016-01-22)
==================
- Fix GitLab issue #243, "System allows a user to skip entering values for a required metadata field while uploading a new document"
- Fix GitLab issue #245, "Add multiple metadata not possible"
- Updated Vagrantfile to provision a production box too.


2.0 (2015-12-04)
================
- New source homepage: https://gitlab.com/mayan-edms/mayan-edms
- Update to Django 1.7
- New Bootstrap Frontend UI
- Easier theming and rebranding
- Improved page navigation interface
- Menu reorganization
- Removal of famfam icon set
- Improved document preview generation
- Document submission for OCR changed to POST
- New YAML based settings system
- Removal of auto admin creation as separate app
- Removal of dependencies
- ACL system refactor
- Object access control inheritance
- Removal of anonymous user support
- Metadata validators refactor
- Trash can support
- Retention policies
- Support for sharing indexes as FUSE filesystems
- Clickable preview images titles
- Removal of eval
- Smarter OCR, per page parsing or OCR fallback
- Improve failure tolerance (not all Operational Errors are critical now)
- RGB tags
- Default document type and default document source
- Link unbinding
- Statistics refactor
- Apps merge
- New signals
- Test improvements
- Indexes recalculation after document creation too
- Upgrade command
- OCR data moved to ocr app from documents app
- New internal document creation workflow return a document stub
- Auto console debug logging during development and info during production
- New class based and menu based navigation system
- New class based transformations
- Usage of Font Awesome icons set
- Management command to remove obsolete permissions: `purgepermissions`
- Normalization of 'title' and 'name' fields to 'label'
- Improved API, now at version 1
- Invert page title/project name order in browser title
- Django's class based views pagination
- Reduction of text strings
- Removal of the CombinedSource class
- Removal of default class ACLs
- Removal of the ImageMagick and GraphicsMagick converter backends
- Remove support for applying roles to new users automatically
- Removal of the DOCUMENT_RESTRICTIONS_OVERRIDE permission
- Removed the page_label field


1.1.1 (2015-05-21)
==================

- Update to Django 1.6.11
- Fix make_dist.sh script
- Add test for issue #163
- Activate tests for the sources app
- Removal of the registration app
- New simplified official project description
- Improvements to the index admin interface
- Removal of installation statistics gathering
- Remove unused folder tag
- Fix usage of ugettext to ugettext_lazy
- Increase size of the lock name field
- New style documentation


1.1 (2015-02-10)
================
- Uses Celery for background tasks
- Removal of the splash screen
- Adds a home view with common function buttons
- Support for sending and receiving documents via email
- Removed custom logging app in favor of django-actvity-stream
- Adds watch folders
- Includes Vagrant file for unified development and testing environments
- Per user locale profile (language and timezone)
- Includes news document workflow app
- Optional and required metadata types
- Improved testings. Automated tests against SQLite, MySQL, PostgreSQL
- Many new REST API endpoints added
- Simplified text messages
- Improved method for custom settings
- Addition of CORS support to the REST API
- Per document language setting instead of per installation language setting
- Metadata validation and parsing support
- Start of code updates towards Python 3 support
- Simplified UI
- Stable PDF previews generation
- More technical documentation


1.0 (2014-08-27)
================
- New home @ https://github.com/mayan-edms/mayan-edms
- Updated to use Django 1.6
- Translation updates
- Custom model properties removal
- Source code improvements
- Removal of included 3rd party modules
- Automatic testing and code coverage check
- Update of required modules and libraries versions
- Database connection leaks fixes
- Support for deletion of detached signatures
- Removal of Fabric based installations script
- Pluggable OCR backends
- OCR improvements
- License change, Mayan EDMS in now licensed under the Apache 2.0 License
- PyPI package, Mayan EDMS in now available on PyPI: https://pypi.python.org/pypi/mayan-edms/
- New REST API
