django-egaxegax
===============

[http://egaxegax.appspot.com] full source code. Google Appengine Python Django-nonrel website project.

Contains apps:

* Blog with Markdown syntax support
* Foto view, upload, download images
* Songs, Books read, add texts

RU: Содержит блог с поддержкой синтаксиса Markdown, хранилище фотографий.

## Install

To run local version install python27 and modules PIL, Pillow.
Download and unpack google-appengine package 1.9.x. 
Set environment and run as standart Django's project. E.g. in Windows shell:

    set PATH=c:\Python27;%PATH%
    set PATH=..\google_appengine;%PATH%
    python manage.py runserver 8080

Try in browser http://127.0.0.1:8080/
