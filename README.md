# SnyPy Backend

[![Known Vulnerabilities](https://snyk.io/test/github/nezhar/snypy-backend/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/nezhar/snypy-backend?targetFile=requirements.txt)
[![codebeat badge](https://codebeat.co/badges/636a710b-e6c6-4ca8-ab1b-921bbaa6c816)](https://codebeat.co/projects/github-com-nezhar-snypy-backend-master)

This project is build using Django 2.0 and Django Rest Framework

# In Development

This project is currently in an early stage of development and is missing lots of features as well as documentation.


# Export Fixture:

```
python manage.py dumpdata auth --natural-foreign --natural-primary -e auth.Permission --indent 4 > fixtures/permissions.json
```

```
python manage.py dumpdata snippets --natural-foreign --natural-primary -e snippets.Snippet -e snippets.File -e snippets.Label -e snippets.SnippetLabel --indent 4 > fixtures/languages.json
```
