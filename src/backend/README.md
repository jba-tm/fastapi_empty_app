Babel translations files

    pybabel extract . -o locale/base.pot -F babel-mapping.ini
    
    # init language
    pybabel init -l ru -i locale/base.pot -d locale
    pybabel init -l tk -i locale/base.pot -d locale
    pybabel init -l en -i locale/base.pot -d locale
    
    # update language
    pybabel update -l en -i locale/base.pot -d locale
    pybabel update -l ru -i locale/base.pot -d locale
    pybabel update -l tk -i locale/base.pot -d locale

    pybabel compile -d locale

Install linux packages:

    apt install libwebp-dev libmagic1# sale_fastapi_backend
