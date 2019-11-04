:: Скрипт разбивает текстовые файлы (тексты песен с аккордами) в подкаталогах
:: в файл выгрузки для GAE DataStore. 
::
:: PTEXT.BAT <Имя каталога> <N начало> <N конец>

@echo off
chcp 1251 > nul
if "%~1"=="" findstr "^::" "%~f0" 1>&2 & GOTO:EOF
set num=0
set key=62001
set nstart=%2
set nstop=%3
:: egax
set author=39001
for /f "tokens=1* delims=[]" %%e in ('dir /a-d /s /b "%1"^|find /n /v ""') do (
  if /i %%e geq %nstart% (
    if /i %%e leq %nstop% (
      pushd "%%~pf"
      for /f "tokens=*" %%g in ('chdir') do (
        if %%e==%nstart% echo artist,title,content,key,date,author_id,audio
        echo|set /p=^""%%~ng^",^"%%~nf",^"^"
        for /f "tokens=1* delims=] skip=2" %%i in ('find /n /v ""^<"%%f"^') do echo/%%j
        for /f "tokens=*" %%a in ('date /t') do set td=%%a
        for /f "tokens=*" %%a in ('time /t') do set tm=%%a
        call set /a key1=%%key%%+%%nstart%%+%%num%%
        call set /a num=%%num%%+1
        call echo ",%%key1%%,%%td%%%%tm%%,%%author%%,
        echo %%e %%~ng - %%~nf 1>&2
      )
      popd
    )
  )
)