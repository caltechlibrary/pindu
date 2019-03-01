Sidewall<img width="22%" align="right" src=".graphics/tire-sidewall-wikipedia.svg">
=============

_Sidewall_ is a Python library for interacting with the [Dimensions](https://app.dimensions.ai) search API.  It defines object classes for various Dimensions data types, fetches data incrementally, copes with rate limits, and more, to help working with Dimensions more natural for Python programmers.

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/caltechlibrary/sidewall](https://github.com/caltechlibrary/sidewall)<br>
*License*:      BSD/MIT derivative &ndash; see the [LICENSE](LICENSE) file for more information

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.5+-brightgreen.svg?style=flat-square)](http://shields.io)
[![Latest version](https://img.shields.io/badge/Latest_version-0.0.1-b44e88.svg?style=flat-square)](http://shields.io)

☀ Introduction
-----------------------------

[Dimensions](https://app.dimensions.ai) offers a networked API and search language (the [DSL](https://docs.dimensions.ai/dsl/language.html)).  However, there is as yet no object-oriented API library for Python.  Interacting with the DSL currently requires sending a search string to the Dimensions server, then interpreting the JSON results and handling various issues such as iterating to obtain more than 1000 values (which requires the use of multiple queries), staying within API rate limits, and more.  _Sidewall_ provides a higher-level interface for working more conveniently with the Dimensions DSL and network API.  Features of Sidewall include:

* object classes defined for different Dimensions data entities
* object attribute values filled in automatically behind the scenes
* lists returned as efficient generators that fetch data over the net as needed
* automatic caching of search results for speed and efficiency
* automatic throttling to keep within API rate limits

"Sidewall" is a loose acronym for _**Si**mple **D**im**e**nsions **w**r**a**pper c**l**ient **l**ibrary_.

✺ Installation instructions
---------------------------

The following is probably the simplest and most direct way to install this software on your computer:
```sh
sudo python3 -m pip install git+https://github.com/caltechlibrary/sidewall.git --upgrade
```

Alternatively, you can clone this GitHub repository and then run `setup.py`:
```sh
git clone https://github.com/caltechlibrary/sidewall.git
cd sidewall
sudo python3 -m pip install . --upgrade
```

▶︎ Using Sidewall
----------------

Sidewall is meant to be used from other programs; it does not provide a standalone command-line interface or graphical user interface.  At this time, Sidewall only supports certain kinds of Dimensions queries as discussed below.


### Basic setup and use

To use Sidewall, import the package and the symbol `dimensions` in your Python code:

```python
import sidewall
from sidewall import dimensions
```

In case of problems, it may be useful to turn on debugging in Sidewall to see everything that is happening behind the scenes.  You can do that by using `set_debug()` after importing Sidewall:

```python
sidewall.set_debug(True)
```

To run queries, you will need first to have an [account with Dimensions](https://plus.dimensions.ai/support/solutions/articles/23000013103-how-can-i-get-an-individual-login-for-dimensions-and-what-can-i-do-with-this-).  There are multiple ways of supplying user credentials to Sidewall.  The simplest and most direct is to supply a user name and password to the `login()` method:

```python
dimensions.login(username = 'somelogin', password = 'somepassword')
```

However, a more secure and more convenient way is to invoke the `login()` method without any arguments:

```python
dimensions.login()
```

When done this way, Sidewall will use the operating system's keyring/keychain functionality to get the user name and password.  If the information does not exist from a previous call to `dimensions.login()`, Sidewall will ask you for the user name and password interactively, and then store it in the keyring/keychain for next time.


### Basic principles of running queries

Sidewall defines a method, `query()`, which you can use to run a search in Dimensions and get back a list of data objects.  The method takes a single argument, a string.  Here is an example:

```python
(total, records) = dimensions.query('search publications for "SBML" return publications')
```

The form of the search query string that Sidewall can use is limited in ways described shortly.  The `query()` method returns multiple values: an integer representing the total number of results returned by the query, and the results themselves.  The latter is in the form of a Python generator so that you iterate over the results or do other operations like a typical Python data generator.

The objects returned by the generator will be Sidewall objects of the kind discussed in the section below on [Data mappings]().  The specific classes of objects returned will correspond to the type of record expressed in the tail end of the query handed to `query()`.  For example, a query that ends in `return publications` will produce Sidewall `Publications` objects; a query that ends in `return researchers` will produce Sidewall `Researcher` objects; and so on.

Sidewall currently puts the following limitations on the form of the query search string:
* it must begin with `search`
* it must end with `return publications`, `return researchers`, or `return grants`
* it must only return a single type of thing (i.e., researchers _or_ publications _or_ grants)
* it must not put facet specifiers or limits on the returned results
* it must not use aggregation or other advanced DSL features

The following is a complete example of using Sidewall to search for publications containing thes string "SBML", and then printing the year and DOI for each such publication found:

```python
import sidewall
from sidewall import dimensions

dimensions.login()
(total, records) = dimensions.query('search publications for "SBML" return publications')

print('Total found: {}'.format(total))
for r in records:
    print('{}: {}'.format(r.year, r.doi))
```


### Data mappings

Sidewall defines object classes such as `Researcher`, `Publication`, and a few others to represent the different types of entities returned as the results of a Dimensions search query.  Sidewall's objects attempt to smooth over some of the confusing aspects of the data representations in Dimensions by providing single objects that consolidate different fields and facets of the same underlying "thing".  Further, the fields of an object sometimes are not available from a given query Dimensions performed by the user but _may_ be available if a _different_ kind of query is performed; Sidewall uses this knowledge in some cases to expand object field values automatically and behind the scenes as needed.

The following data classes are defined by Sidewall at this time; note that this is not all the types of data that Dimensions provides today, but future work may improve Sidewall's coverage.

* `Person`, with subclasses `Authors` and `Researchers`
* `Organization`
* `Publication`
* `Journal`


**_Person_**

Dimensions doesn't expose an underlying base class for people; instead, it returns unnamed data structures that basically refer to people in different contexts.  Sidewall currently understands two such contexts: authors of publications (when a query uses `return publications`), and "researchers" (when a query uses `return researchers`).  Sidewall introduces a parent class called `Person` because the objects in these two contexts are so similar, and provides two derived classes: `Author` and `Researcher`.  The distinction provided by the derived classes is necessary because **the list of affiliations for an `Author` is relative to a particular publication and may not be all the affiliations that a person has**.  Thus, affiliations for others must be understood in the context of a particular search for publications.

```
           ┌──────────────┐
           │    Person    │
           └──────────────┘
                  ^
        ┌─────────┴──────────┐
┌───────┴──────┐      ┌──────┴───────┐
│    Author    │      │  Researcher  │
└──────────────┘      └──────────────┘
```

The following table describes the fields and how they relate to values returned from Dimensions:

|   Field                | In "return researchers"? | In "return publications"?      | Sidewall expanded? |
|------------------------|--------------------------|--------------------------------|--------------------|
| `affiliations`         | as `research_orgs`       | y                              | y                  |
| `current_organization` | n                        | via `current_organization_id`  | y                  |
| `first_name`           | y                        | y                              | n                  |
| `id`                   | y                        | as `researcher_id`             | n                  |
| `last_name`            | y                        | y                              | n                  |
| `orcid`                | as `orcid_id`            | y                              | n                  |
                                      
The `affiliations` field in Sidewall's `Person` (and consequently `Author` and `Researcher`) is a list of `Organization` class objects (see below).  Although affiliations as returned by Dimensions are sparse when using a query that ends with `return researchers` (they consist only of organization identifiers), Sidewall hides this by providing complete `Organization` objects for the `affiliations` field of a `Person`, and using behind-the-scenes queries to Dimensions to fill out the organization info when the object field values are accessed.  Thus, calling programs do not need to do anything to get organization details in a result regardless of whether they use `return publications` or `return researchers`&mdash;Sidewall always provides `Organization` class objects and handles getting the field values automatically.

`Author` class objects are returned when returning publication results, and in those cases, the list of a person's affiliations will reflect their affiliations with respect to a particular publication.  However, sometimes it's convenient to get more information about an author.  Sidewall allows you to create a `Researcher` object out of an `Author` object for just that reason.  Here is an example to illustrate the differences between authors and researchers and how you can conver the former to the latter:





**_Organization_**

The following table describes the fields and how they relate to values returned from Dimensions:

|   Field         | In "return research_orgs"? | In "return publications"? | Sidewall expanded? |
|-----------------|----------------------------|---------------------------|--------------------|
| `acronym`       | y                          | n                         | y                  |
| `city`          | n                          | y                         | n                  |
| `city_id`       | n                          | y                         | n                  |
| `country`       | n                          | y                         | n                  |
| `country_code`  | n                          | y                         | n                  |
| `country_name`  | y                          | n                         | y                  |
| `id`            | y                          | y                         | n                  |
| `name`          | y                          | y                         | n                  |
| `state`         | n                          | y                         | n                  |
| `state_code`    | n                          | y                         | n                  |


**_Publication_**



⁇ Getting help and support
--------------------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/sidewall/issues) for this repository.


☺︎ Acknowledgments
-----------------------

The [vector artwork](https://commons.wikimedia.org/wiki/File:Tire_code_-_en.svg) of a car tire used as a logo for this repository was created by [Flanker](https://commons.wikimedia.org/wiki/User:F_l_a_n_k_e_r).  It is licensed under the Creative Commons [Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/deed.en) license.

☮︎ Copyright and license
---------------------

Copyright (C) 2019, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src=".graphics/caltech-round.svg">
  </a>
</div>
