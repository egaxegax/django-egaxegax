django-egaxegax
===============

[egaxegax.appspot.com](http://egaxegax.appspot.com) full source code. Google Appengine Python Django-nonrel website project.

![](https://content-11.foto.my.mail.ru/bk/egax/_cover/b-74.jpg)

Contains apps:

* Blog with Markdown syntax support
* Foto view, upload, download images
* Songs, Books read, add texts

RU: Содержит блог с поддержкой синтаксиса Markdown, хранилище фотографий.

## Install and run

To run local version install python27.<br>
Download and install the Google Cloud SDK.<br>
Set environments and run as standart Django project. E.g. in Windows shell:

    set PATH=%PATH%;c:\Python27;..\GoogleCloudSDK\google-cloud-sdk\platform\google_appengine
    python manage.py runserver 8080

or run from gcloud shell

    dev_appserver django-egaxegax

Try in browser http://127.0.0.1:8080/
