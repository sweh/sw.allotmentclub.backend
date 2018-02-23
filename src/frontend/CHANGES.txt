===============================
Change log for sw.allotmentclub
===============================

4.0.1 (2018-02-23)
==================

- Remove app-init stuff which was needed by the heroku nginx buildpack.

- Update netatmo client and scope it to only read station data.

- Retrieve banking credentials from pyramid settings instead of from the environment.


4.0.0 (2018-02-15)
==================

- Add compiled frontend code into package.


3.9.0 (2018-02-14)
==================

- Fix install requirements to be able to install them only from pypi.


3.8.0 (2018-02-13)
==================

- Prepare package for the first release on Pypi.


3.7.6 (2018-01-31)
==================

- Print firstname in the signature of letters.


3.7.5 (2018-01-31)
==================

- Print firstname in the signature of mails.


3.7.4 (2018-01-15)
==================

- Fix length validator if value is None.

- Fix import of Rechnungen. Be more verbose if import is broken.


3.7.3 (2018-01-14)
==================

- Fix tests.


3.7.2 (2018-01-14)
==================

- Fix brown bag release.


3.7.1 (2018-01-14)
==================

- Increase time to look back when importing transactions.


3.7.0 (2017-12-22)
==================

- Add validation to most of the form fields.


3.6.1 (2017-12-21)
==================

- Dont save messages sent via application in inbox.


3.6.0 (2017-12-21)
==================

- Show waste water list in application.

- Show property tax b list in application.

- Show energy price values.


3.5.2 (2017-12-05)
==================

- Add vorstand@roter-see.de as CC if mail is sent to just one recipient.


3.5.1 (2017-11-18)
==================

- Fix bug in assigment update form.

- Remove SW from Ende in protocols.

- Add protocol attachment delete view.


3.5.0 (2017-11-08)
==================

- Add member add form.


3.4.9 (2017-11-06)
==================

- Add empty title to external recipients.


3.4.8 (2017-11-03)
==================

- Add a mask icon which gets rendered in Safari pinned tabs.


3.4.7 (2017-10-12)
==================

- Prepare Energieabrechnung 2017.


3.4.6 (2017-09-20)
==================

- Add access for eberhard kietz as Behoerdenbeauftragter.


3.4.5 (2017-09-18)
==================

- Use `mt-940` egg instead of checkout as changes are released now.

- Dont be too strict when rendering PDFs.

- Make protocoll details more robust against wrong user input.


3.4.4 (2017-09-01)
==================

- Repair tests.


3.4.3 (2017-09-01)
==================

- Allow adding MS Word documents and images to mails as attachments.


3.4.2 (2017-08-24)
==================

- Fix bug in generating frontend sources.


3.4.1 (2017-08-24)
==================

- Updated frontend libraries.


3.4.0 (2017-08-22)
==================

- Energieabrechnung is now a ful integrated workflow.


3.3.8 (2017-08-21)
==================

- Fix inbound webhook special date.


3.3.7 (2017-08-18)
==================

- Just retrieve bookings from the last 7 days.


3.3.6 (2017-08-17)
==================

- Add missing frontend images.


3.3.5 (2017-08-17)
==================

- Fix postmark inbound webhook if attachment has a long mimetype.


3.3.4 (2017-08-17)
==================

- No longer raise Exception if SentMessageInfo is non as this results in recursive errors.


3.3.3 (2017-08-17)
==================

- No longer raise Exception if SentMessageInfo is non as this results in recursive errors.


3.3.2 (2017-08-17)
==================

- Fix syntax error in portal.ini.


3.3.1 (2017-08-17)
==================

- Send exceptions per mail.


3.3.0 (2017-08-16)
==================

- Update pyramid to version 1.9.1.


3.2.11 (2017-08-07)
===================

- Add HTML parser for incoming mail.


3.2.10 (2017-07-28)
===================

- Add signature for hs.


3.2.9 (2017-07-27)
==================

- Add fallback if netatmo API is not working.


3.2.8 (2017-07-23)
==================

- Repair download of protocol attachments after upgrade to Python 3.6.

- Decrease font size of bulletins from 20pt to make room for more content.


3.2.7 (2017-07-16)
==================

- Fix duplicate import of SAMMLER-LS.


3.2.6 (2017-07-04)
==================

- Fix import of SAMMLER-LS.


3.2.5 (2017-06-22)
==================

- Change Vorsitzender in all letters to the current one.


3.2.4 (2017-06-19)
==================

- Look wider in the history when retrieving fints items.


3.2.3 (2017-06-19)
==================

- Add new users Andreas Mielke and Constanze Seyfert.


3.2.2 (2017-06-16)
==================

- Use `babel` to format currencies and translate datetimes OS independent.


3.2.1 (2017-06-15)
==================

- Revert back to localized datime and currency formatting as problems on heroku side are solved.


3.2.0 (2017-06-14)
==================

- Update to Pyramid 1.8.4.

- Use the python library `fints` to replace the old `aqbanking` script.


3.1.2 (2017-06-09)
==================

- Add a reply view for messages.

- Use `pytest-catchlog` in favor of `pytest-capturelog` which is no longer maintained.

- Switch to XSLX export for Zählerstände and Einladungsliste MV.

- Fixed download of Betritt and Lastschrift.


3.1.1 (2017-05-30)
==================

- Fix member edit for after switch to Python3.

- Add more debugging output for delivery webhook.


3.1.0 (2017-05-26)
==================

- Fix error if no IP was sent in Postmark webkook.

- Add mail inbox and split old mail view into sent and drafts.


3.0.0 (2017-05-24)
==================

- Bump python version from Python 2.7 to Python 3.6.
  3.6


2.12.0 (2017-05-16)
===================

- Bump all versions of packages to the newest ones.


2.11.1 (2017-05-12)
===================

- Fix tests on circleCI.


2.11.0 (2017-05-12)
===================

- Add upport for delivery postmark webhook.

- Add postmark inbound webhook.


2.10.9 (2017-04-27)
===================

- Readd codecov upload (JS) as its no longer broken for circleci.


2.10.8 (2017-03-22)
===================

- No longer display members and users from different organizations in dropdowns.


2.10.7 (2017-03-16)
===================

- Remove codecov upload (JS) as its broken for circleci.


2.10.6 (2017-03-16)
===================

- Fix a bug in deployment process.


2.10.5 (2017-03-16)
===================

- Set member Beitrag to 65,- EUR.

- Increase proxy cache so that the map renders correctly.


2.10.4 (2017-03-09)
===================

- Fix a bug where mails were sent to people in the wrong organization.


2.10.3 (2017-02-21)
===================

- Fix segmentation fault during transaction import.

- No longer reimport transaction before 2017.


2.10.2 (2017-02-07)
===================

- Fix access to other vcf addressbook data.


2.10.1 (2017-02-07)
===================

- Add organization name to vcf addressbook data.


2.10.0 (2017-02-07)
===================

- Support multiple organizations when writing vcf addressbook data.


2.9.0 (2017-02-07)
==================

- Add birthday to members.

- Add script to import members from CSV.


2.8.4 (2017-01-19)
==================

- Also display rain info of the last 24h.


2.8.3 (2017-01-19)
==================

- Improve visual appearance of current temperature.


2.8.2 (2017-01-19)
==================

- Fix some more display bugs on mobile devices.


2.8.1 (2017-01-19)
==================

- Fix a display bug on mobile devices.


2.8.0 (2017-01-19)
==================

- Display current temperature in dashboard.


2.7.5 (2017-01-11)
==================

- Rollback readonly mode as it is not working correctly.


2.7.4 (2017-01-11)
==================

- Switch DAV to readonly mode.


2.7.3 (2017-01-11)
==================

- Debug non starting CardDAV server.


2.7.2 (2017-01-11)
==================

- Debug non starting CardDAV server.


2.7.1 (2017-01-11)
==================

- Fix tests.


2.7.0 (2017-01-11)
==================

- Add CardDAV-Server that serves member data for CardDAV clients.


2.6.6 (2017-01-09)
==================

- Update webserver for letsencrypt authentication.


2.6.5 (2017-01-09)
==================

- Minor tweaks to the build process.


2.6.4 (2017-01-09)
==================

- Repair release.

- Update webserver for letsencrypt authentication.


2.6.3 (2017-01-04)
==================

- Bugfix while importing splitted Sammler.


2.6.2 (2016-11-28)
==================

- Bugfix: Dont break if no city is given.

- Bugfix: Silence "Zeile markieren" error.


2.6.1 (2016-11-24)
==================

- Bugfix assignment hours billing.


2.6.0 (2016-11-24)
==================

- Update bank information.

- Add support for the postmark bounce webhook.


2.5.4 (2016-11-23)
==================

- Fix the message tag format.

- Display the mail status in a seperate table.


2.5.3 (2016-11-23)
==================

- Fix the timezone of the opened date received by postmark.


2.5.3 (2016-11-23)
==================

- Use tag instead if Message-ID to get the right message from DB.


2.5.3 (2016-11-22)
==================

- Bugfix release.


2.5.2 (2016-11-22)
==================

- Make sure that Postmark keeps the Message-ID Header.


2.5.1 (2016-11-22)
==================

- Raise a more readable error if tracking status sent by postmark cannot be
  saved.


2.5.0 (2016-11-22)
==================

- Save the open tracking status for messages sent via postmark in db.


2.4.0 (2016-11-22)
==================

- Add new view to show, where a member made is assignments.


2.3.1 (2016-10-20)
==================

- Prepare update to letsencrypt certificate again.


2.3.0 (2016-10-20)
==================

- Prepare update to letsencrypt certificate.


2.2.4 (2016-10-20)
==================

- Fix import bug, that different members might have the same iban.


2.2.3 (2016-10-18)
==================

- Bugfix for the duplicate booking fix. (#24)


2.2.2 (2016-10-18)
==================

- Fix duplicate bookings. (#24)


2.2.1 (2016-09-27)
==================

- Fix SEPA export for Energieabrechnung.


2.2.0 (2016-09-16)
==================

- Finalize the new energy billing procedure.


2.1.6 (2016-09-12)
==================

- Improve handling of import and calculation of energy values.

- Add booking details views. (#6)


2.1.5 (2016-08-02)
==================

- Bugfix: Repair automatic account import after changes from #16.


2.1.4 (2016-08-02)
==================

- Bugfix: Repair automatic account import after changes from #16.


2.1.3 (2016-08-02)
==================

- No longer remove duplicate log entries.


2.1.2 (2016-07-31)
==================

- Add information about tap water on parcels. (#21)


2.1.1 (2016-07-30)
==================

- Fixed a bug that prevented load of MemberAccountDetailList after #16.

- Massively improved performance by removing bleach clean on every rendered
  text item.


2.1.0 (2016-07-27)
==================

- Move `insert_due_for_membership_fee` entry point to a view accessable from
  UI. (#3)

- Move `calculate_energy_values` entry point to a view accessable from UI. (#3)

- Its now possible to add different organizations. (#16)

- Minor code clean up.


2.0.5 (2016-07-26)
==================

- Bugfix in fetching transactions from bank. (#10)


2.0.4 (2016-07-25)
==================

- Add attachments for keylists. (#18)

- Add text/plain part in emails. (#20)

- Fix security problem. (#10)


2.0.3 (2016-07-20)
==================

- Update Rollbar integration.

- Start adding OpenCV support.


2.0.2 (2016-07-15)
==================

- Max upload size increased to 10MB.


2.0.1 (2016-07-12)
==================

- Styling fixes.


2.0.0 (2016-07-12)
==================

- Introduce view based security via database. Access to any view can now be
  authorized to single users via a new admin interface.


1.7.1 (2016-07-07)
==================

- Minor bugfixes.


1.7.0 (2016-07-06)
==================

- Add keylist module.


1.6.14 (2016-07-05)
===================

- Improve the load times of the home view.

- Add view that display sale history since 2016.

- Moved letter Energieabrechnung and Fehlende Arbeitsstunden to mail.

- Removed formletter module.


1.6.13 (2016-07-03)
===================

- Repair member account details view after changes to SEPASammler.

- Add view that automatically generates SEPASammler entries for a SEPASammler.

- Add view to export the new SEPASammler to Sparkasse XML.


1.6.12 (2016-06-30)
===================

- Prepare sepa sammler import.


1.6.11 (2016-06-29)
===================

- Begin refactoring the SEPA Sammler views.

- Export email address in MV entrance list.


1.6.10 (2016-06-27)
===================

- Export comment to energy meter list if discounted to a third person.

- Add view to export MV entrance list.

1.6.9 (2016-06-26)
==================

- Improved export of energy meters.

1.6.8 (2016-06-22)
==================

- Use printed date for later downloads of already sent messages.

1.6.7 (2016-06-22)
==================

- Add some more fields to member edit form. (#4)

1.6.6 (2016-06-16)
==================

- Add member edit form. (#4)


1.6.5 (2016-06-16)
==================

- Improved Zaehler-Export:

  - Show the standings of the last 2 years.
  - Dont export the Satellitenanlage virtual Zaehler.

- Permanently fix a bug with sending to big emails via `repoze.sendmail`.

- Change XML downloads to ZIP downloads to be compatible to iOS browsers.

- Allow HTML tables in forms e.g. for Tagesordnung.

1.6.4 (2016-06-14)
==================

- Added seperate views for AdvancePayDownload I and II.


1.6.3 (2016-05-21)
==================

- Add new access group 'Revisionskommission', which has read only access to
  electricity and finances.


1.6.2 (2016-05-11)
==================

- Title and appellation for external recipients where inverted.


1.6.1 (2016-04-27)
==================

- Bugfix: Preview should render pdf of all recipients, not just those without
  an email address.


1.6.0 (2016-04-26)
==================

- Add buttons for CSV download and print to every datatable.


1.5.10 (2016-04-26)
===================

- Bugfix: Dont try to send emails to post addresses, stupid!

- Bugfix: Allow german float format for assignment attendee hours. (re #11)


1.5.9 (2016-04-25)
==================

- Added firstname to available variables for greetings in messages.


1.5.8 (2016-04-25)
==================

- Allow customization of the greeting line in messages.


1.5.7 (2016-04-21)
==================

- Repair Mail-UI sending messages no longer returns an error. (#9)


1.5.6 (2016-04-21)
==================

- Allow adding multiple recipients in Mail.


1.5.5 (2016-04-18)
==================

- Update Vorsitzenden to Annette Rösler in mail and print footer.

- Add signature of Annette Rösler.


1.5.4 (2016-04-13)
==================

- Explicitely save objects on add to the database. This should prevent the
  randomly occurring `AttributeError: 'NoneType' object has no attribute '__acl__'`.
  (https://rollbar.com/sw-allotmentclub/sw-allotmentclub/items/12/)


1.5.3 (2016-04-13)
==================

- Allow Google Chrome to restore saved username/password to login form.


1.5.2 (2016-03-31)
==================

- Add SEPA Sammler für Energieabschlag I and Mitgliedsbeitrag 2016.


1.5.1 (2016-03-30)
==================

- Bugfix: Repair add/edit form of protocols and assignment attendees, which
  broke due to an API change in `ajja` form library that was not handled
  correctly.


1.5.0 (2016-03-30)
==================

- Use new form library `ajja` which is the successor of `gocept.jsform`.

- Allow sending messages to external recipients which are not members of the
  allotmentclub.


1.4.9 (2016-03-17)
==================

- Set DateStyle on Database as the fix from 1.4.8 did not work unfortunately.


1.4.8 (2016-03-17)
==================

- Explicitely set DateStyle for postgresql to fix changing dates in postgres db.


1.4.7 (2016-03-15)
==================

- Only log successful bank imports if transactions were imported.

- Begin cleaning up code base.


1.4.6 (2016-03-14)
==================

- Add Rollbar integration. Now every exception in frontend or backend is
  captured.


1.4.5 (2016-03-14)
==================

- Fixed a bug with the auto source reload feature.


1.4.4 (2016-03-14)
==================

- Members that sold their allotments should not have to pay advance electricity costs.

- Fixed BIC of Andre Hartmann which broke the Saalesparkasse SEPA importer.


1.4.3 (2016-03-10)
==================

- Try to auto reload frontend sources if version does not match.

- Make this Changelog accessable in frontend.


1.4.2 (2016-03-10)
==================

- Fix tests to allow deployment.


1.4.1 (2016-03-10)
==================

- Ease postgresql development setup.

- Add logging for booking import.


1.4.0 (2016-03-09)
==================

- Update requirements to newest versions.

- Bugfix: Readd `pyramid_tm` to repair transaction management.


1.3.8 (2016-03-09)
==================

- Make the import bankings work.


1.3.7 (2016-03-09)
==================

- Add aqbanking as a buildpack.


1.3.6 (2016-03-08)
==================

- Use epoll/kqueue as nginx connection method on supported systems.

- Use shield style for CircleCi token.

- Add code coverage reports for frontend code.

- No longer send emails bcc to vorstand@roter-see.de.

- Provide an aqbanking binary for testing first.

1.3.5 (2016-03-08)
==================

- Fix development setup to have grunt and py.test in the monorepo root.

- Initialize app with nginx correctly.


1.3.4 (2016-03-07)
==================

- Finally repair deployment.


1.3.3 (2016-03-07)
==================

- Repair deployment again.


1.3.2 (2016-03-06)
==================

- Repair deployment again.


1.3.1 (2016-03-06)
==================

- Repair deployment.


1.3.0 (2016-03-06)
==================

- Remove buildout form deployment.


1.2.11 (2016-03-04)
===================

- Add static page content and nginx config for http://www.roter-see.de.


1.2.10 (2016-03-04)
===================

- Added icon to verify SSL grade.

- Add code coverage and icon to measure coverage.

1.2.9 (2016-03-03)
==================

- Add relic application messurements.


1.2.8 (2016-03-03)
==================

- Update DB config.


1.2.6 (2016-03-03)
==================

- Fix map tests.


1.2.5 (2016-03-02)
==================

- Fix nginx server config.


1.2.3 (2016-03-02)
==================

- Remove depencency to `rsvg-convert`.


1.2.2 (2016-03-02)
==================

- Enable Mail on Heroku.


1.2.0 (2016-03-02)
==================

- Update build to use `pip` to install requirements.

- Prepare releasing to Heroku.


1.1.1 (2016-03-01)
==================

- Add CI badge in footer.


1.1.0 (2016-03-01)
==================

- Write tests in `py.test` and `jasmine`.

- Move from mercurial to github.


1.0.10 (2016-02-29)
===================

- Fix filename ending for depot downloads.


1.0.9 (2016-02-22)
==================

- Implement sorting for kilowatthours.

1.0.7 (2016-02-03)
==================

- Add view for allotment sale from one member to another.

- Allow specifying an account holder different from owner of allotment for
  direct debit.

1.0.6 (2016-02-03)
==================

- Fix duplicate names in map view.

- Improve rendering of version mismatch error message. Add hint what to do to
  get rid of this message.

- Updated form library to newest major version (gocept.jsform == 3.0.0)


1.0.5 (2016-02-02)
==================

- Began writing Changelog.

- Add version check between client and server to make sure client uses newest
  software version available.

- Add automatic import from banking account.
