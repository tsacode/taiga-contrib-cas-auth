Taiga contrib cas auth
=========================
The Taiga plugin for cas authentication (Ported from official cas auth).

Installation
------------
### Production env

#### Taiga Back

Clone the repo and

```bash
cd taiga-contrib-cas-auth/back
  workon taiga (if different, the name of taiga-virtualenv)
  python setup.py sdist
  pip install dist/taiga-contrib-cas-auth-1.0.tar.gz
```

Modify taiga-back/settings/local.py and include the lines:

```python
  INSTALLED_APPS += ["taiga_contrib_cas_auth"]

  CAS_URL = "your CAS url"
  # for settings
  # if your CAS attributes are generic ('id', "full_name", "email", "bio") you don't need to define them below
  # though CAS_FIELD should at least be equal to {}
  CAS_FIELD = {
              "id": "corresponding CAS attribute",
              "full_name": "corresponding CAS attribute",
              "email": "corresponding CAS attribute",
              "bio": "corresponding CAS attribute"
              }
  # when true allows Taiga to register new user from CAS
  CAS_CREATE = True
  # when true allows Taiga to overwrite data of Taiga account with CAS's account data
  CAS_OVERWRITE = True
  # when true allows Taiga to bind existing taiga account to CAS account
  CAS_BIND = True
```
#### Taiga Front

After clone the repo link `dist` in `taiga-front` plugins directory:

```bash
  cd taiga-front-dist/dist
  mkdir -p plugins
  cd plugins
  ln -s ../../../taiga-contrib-cas-auth/front/dist cas-auth
```

Include in your `dist/conf.json` casUrl and in the 'contribPlugins' list the value `"/plugins/cas-auth/cas-auth.json"`:

```json
...
    "casUrl": "YOUR-CAS-URL",
    "contribPlugins": [
        (...)
        "/plugins/cas-auth/cas-auth.json"
    ]
...
```

for i18n:

```bash
  cd taiga-front-dist/v-............./locales
  ln -s ../../plugins/cas-auth/locales/ cas-auth
```
for make .po file for a langage that'not supported
```bash
msginit --input=i18n/services.pot --output=i18n/lang/LC_MESSAGES/services.po
```
translate the strings then make the .mo file :
```bash
msgfmt i18n/lang/LC_MESSAGES/services.po --output-file i18n/lang/LC_MESSAGES/services.mo
```
### Dev env

#### Taiga Back

Clone the repo and

```bash
  cd taiga-contrib-cas-auth/back
  workon taiga
  pip install -e .
```

Modify `taiga-back/settings/local.py` and include the lines:

```python
  INSTALLED_APPS += ["taiga_contrib_cas_auth"]

  CAS_URL = "your CAS url"
  # for settings
  # if your CAS attributes' names are generic ('id', "full_name", "email", "bio") you don't need to define them below
  # though CAS_FIELD should at least be equal to {}
  CAS_FIELD = {
              "id": "corresponding CAS attribute",
              "full_name": "corresponding CAS attribute",
              "email": "corresponding CAS attribute",
              "bio": "corresponding CAS attribute"
              }
  # when true allows Taiga to register new user from CAS
  CAS_CREATE = True
  # when true allows Taiga to synchronize data of Taiga account with CAS's account data
  CAS_OVERWRITE = True
  # when true allows Taiga to bind existing taiga account to CAS account
  CAS_BIND = True

```

#### Taiga Front

After clone the repo link `dist` in `taiga-front` plugins directory:

```bash
  cd taiga-front/dist
  mkdir -p plugins
  cd plugins
  ln -s ../../../taiga-contrib-cas-auth/front/dist cas-auth
```

Include in your `dist/conf.json` casUrl and in the 'contribPlugins' list the value `"/plugins/cas-auth/cas-auth.json"`:

```json
...
    "casUrl": "YOUR-CAS-URL",
    "contribPlugins": [
        (...)
        "/plugins/cas-auth/cas-auth.json"
    ]
...
```

for i18n:

```bash
  cd taiga-front/app/modules
  mkdir -p compile-modules/cas-auth
  ln -s ../../../taiga-contrib-cas-auth/front/dist/locales/ compile-modules/cas-auth/locales
```

for make .po file for a langage that'not supported
```bash
msginit --input=i18n/services.pot --output=i18n/lang/LC_MESSAGES/services.po
```
translate the strings then make the .mo file :
```bash
msgfmt i18n/lang/LC_MESSAGES/services.po --output-file i18n/lang/LC_MESSAGES/services.mo
```

In the plugin source dir `taiga-contrib-cas-auth/front` run

```bash
npm install
```
and use:

- `gulp` to regenerate the source and watch for changes.
- `gulp build` to only regenerate the source.


Running tests
-------------

We only have backend tests, you have to add your `taiga-back` directory to the
PYTHONPATH environment variable and work with the virtualenv of taiga
```bash
  cd back/tests
  workon taiga
  python3 -m unittest
```