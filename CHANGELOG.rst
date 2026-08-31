
Changelog
=========

0.7.0 (2026-08-30)
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
* Ship the immutable CFDI product/service database in Python distributions and
  preserve immutable catalog results across Python and TypeScript runtimes.
* Return an explicit catalog version on every Worker JSON response so payroll
  and CRM clients can reject unversioned catalog data.
* Publish through short-lived OIDC credentials for PyPI, npm, and pub.dev, and
  through the Sonatype Central Portal for Maven.

0.2.0 (2016-10-02)
-----------------------------------------

* First release on PyPI.
