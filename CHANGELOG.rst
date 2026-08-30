
Changelog
=========

0.7.0 (unreleased)
-----------------------------------------

* Require the last registered monthly SBC when calculating Modalidad 40.
* Select IMSS minimum-wage and CEAV rules by exercise, effective date, and
  ``general`` or ``frontera`` wage zone.
* Mark Modalidad 10 as ``legacy_unverified`` and keep it disabled in the public
  calculator pending its source audit.
* Package runtime JSON catalogs for Node consumers and provide an explicit
  small-catalog preload for browser and Cloudflare Worker consumers.
* Add a distinct Worker-safe CFDI Nómina profile for the SAT-mandated
  ``84111505`` product/service key without presenting the full catalog as loaded.
* Publish equivalent fiscal-manifest accessors in Python and TypeScript.

0.2.0 (2016-10-02)
-----------------------------------------

* First release on PyPI.
