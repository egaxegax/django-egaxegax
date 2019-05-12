django-egaxegax
===============

[egaxegax.appspot.com](http://egaxegax.appspot.com) full source code. Google Appengine Python Django-nonrel website project.

![](https://content-11.foto.my.mail.ru/bk/egax/_cover/b-74.jpg)

Contains apps:

* Blog with Markdown syntax support
* Foto view, upload, download images
* Songs, Books read, add texts

RU: Содержит блог с поддержкой синтаксиса Markdown, хранилище фотографий.

## Install

To run local version install python27 and module Pillow (former PIL).<br>
Download and install the original App Engine SDK for Python (google_appengine_1.9.x.zip).<br>
Set environment and run as standart Django project. E.g. in Windows shell:

    set PATH=c:\Python27;%PATH%
    set PATH=..\google_appengine;%PATH%
    python manage.py runserver 8080

Try in browser http://127.0.0.1:8080/
